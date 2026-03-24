from collections import defaultdict
from urllib.parse import urljoin, urldefrag, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import requests

from crawler.links import normalize_link
from rules.seo_rules import (
    DUPLICATE_META_DESCRIPTION,
    DUPLICATE_TITLE,
    ISSUE_DUPLICATE_META_DESCRIPTION,
    ISSUE_DUPLICATE_TITLE,
)


ISSUE_REDIRECTED = "redirected"
ISSUE_NON_200_STATUS = "non_200_status"
ISSUE_CANONICAL_MISSING = "canonical_missing"
ISSUE_CANONICAL_DIFFERENT = "canonical_different"
ISSUE_META_NOINDEX = "meta_noindex"
ISSUE_X_ROBOTS_NOINDEX = "x_robots_noindex"
ISSUE_BLOCKED_BY_ROBOTS = "blocked_by_robots"
ISSUE_BROKEN_INTERNAL_LINKS = "broken_internal_links"
ISSUE_UNVERIFIED_INTERNAL_LINKS = "unverified_internal_links"

ROBOTS_USER_AGENT = "SEO-Audit-App/1.0"


def normalize_url(url):
    if not url:
        return None

    normalized, _ = urldefrag(url.strip())
    parsed = urlsplit(normalized)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    query = parsed.query
    return urlunsplit((scheme, netloc, path, query, ""))


def build_issue(code, message):
    return {"code": code, "message": message}


def parse_x_robots_tag(headers):
    header_value = headers.get("X-Robots-Tag") or headers.get("x-robots-tag") or ""
    directives = {directive.strip().lower() for directive in header_value.split(",") if directive.strip()}
    return header_value.strip() or None, directives


def load_robots_rules(site_url, timeout=10):
    robots_url = urljoin(site_url.rstrip("/") + "/", "robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        response = requests.get(
            robots_url,
            headers={"User-Agent": ROBOTS_USER_AGENT},
            timeout=timeout,
        )

        if response.status_code != 200:
            return {
                "url": robots_url,
                "available": False,
                "status_code": response.status_code,
                "parser": None,
            }

        parser.parse(response.text.splitlines())
        return {
            "url": robots_url,
            "available": True,
            "status_code": response.status_code,
            "parser": parser,
        }

    except requests.exceptions.RequestException:
        return {
            "url": robots_url,
            "available": False,
            "status_code": None,
            "parser": None,
        }


def is_allowed_by_robots(robots_rules, url):
    parser = robots_rules.get("parser")
    if not parser:
        return True
    return parser.can_fetch(ROBOTS_USER_AGENT, url)


def evaluate_technical_seo(requested_url, page, footprint):
    technical_issues = []
    final_url = page.get("final_url") or requested_url
    status_code = page.get("status_code")
    headers = page.get("headers", {})
    canonical_url = footprint.get("canonical_url")
    normalized_final_url = normalize_url(final_url)
    normalized_canonical_url = normalize_url(canonical_url)
    x_robots_tag, x_robots_directives = parse_x_robots_tag(headers)

    if page.get("redirected"):
        technical_issues.append(
            build_issue(ISSUE_REDIRECTED, f"Page redirected to {final_url}")
        )

    if status_code != 200:
        technical_issues.append(
            build_issue(ISSUE_NON_200_STATUS, f"Page returned status {status_code}")
        )

    if not footprint.get("canonical_present"):
        technical_issues.append(build_issue(ISSUE_CANONICAL_MISSING, "Missing canonical tag"))
        canonical_status = "missing"
    elif normalized_canonical_url == normalized_final_url:
        canonical_status = "self"
    else:
        technical_issues.append(
            build_issue(
                ISSUE_CANONICAL_DIFFERENT,
                f"Canonical points to {canonical_url}",
            )
        )
        canonical_status = "different"

    if footprint.get("robots_noindex"):
        technical_issues.append(build_issue(ISSUE_META_NOINDEX, "Meta robots contains noindex"))

    if "noindex" in x_robots_directives:
        technical_issues.append(
            build_issue(ISSUE_X_ROBOTS_NOINDEX, "X-Robots-Tag contains noindex")
        )

    return {
        "final_url": final_url,
        "redirected": page.get("redirected", False),
        "redirect_count": page.get("redirect_count", 0),
        "canonical_status": canonical_status,
        "canonical_url": canonical_url,
        "meta_robots": footprint.get("robots_meta_content"),
        "x_robots_tag": x_robots_tag,
        "indexable": not footprint.get("robots_noindex") and "noindex" not in x_robots_directives,
        "issues": technical_issues,
        "robots_allowed": True,
        "broken_internal_links_count": 0,
        "broken_internal_link_samples": [],
        "unverified_internal_links_count": 0,
        "unverified_internal_link_samples": [],
    }


def build_robots_blocked_result(url, footprint, robots_rules):
    issue = build_issue(
        ISSUE_BLOCKED_BY_ROBOTS,
        f"Blocked by robots.txt: {robots_rules.get('url')}",
    )

    return {
        "final_url": url,
        "redirected": False,
        "redirect_count": 0,
        "canonical_status": "unknown",
        "canonical_url": footprint.get("canonical_url"),
        "meta_robots": None,
        "x_robots_tag": None,
        "indexable": None,
        "issues": [issue],
        "robots_allowed": False,
        "broken_internal_links_count": 0,
        "broken_internal_link_samples": [],
        "unverified_internal_links_count": 0,
        "unverified_internal_link_samples": [],
    }


def append_duplicate_metadata_issues(results):
    title_map = defaultdict(list)
    meta_map = defaultdict(list)

    for result in results:
        title = (result.get("seo_data", {}).get("title") or "").strip().lower()
        meta_description = (result.get("seo_data", {}).get("meta_description") or "").strip().lower()

        if title:
            title_map[title].append(result)
        if meta_description:
            meta_map[meta_description].append(result)

    for duplicates in title_map.values():
        if len(duplicates) < 2:
            continue
        sample_urls = ", ".join(page["url"] for page in duplicates[:3])
        for result in duplicates:
            result["issues"].append(f"{DUPLICATE_TITLE} ({sample_urls})")
            result["issue_codes"].append(ISSUE_DUPLICATE_TITLE)

    for duplicates in meta_map.values():
        if len(duplicates) < 2:
            continue
        sample_urls = ", ".join(page["url"] for page in duplicates[:3])
        for result in duplicates:
            result["issues"].append(f"{DUPLICATE_META_DESCRIPTION} ({sample_urls})")
            result["issue_codes"].append(ISSUE_DUPLICATE_META_DESCRIPTION)


def check_link_status(url, timeout=5):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": ROBOTS_USER_AGENT},
            timeout=timeout,
            allow_redirects=True,
        )
        return response.status_code
    except requests.exceptions.RequestException:
        return None


def append_broken_internal_link_issues(results, max_links_to_check=250):
    urls_to_check = []
    seen = set()

    for result in results:
        for link in result.get("internal_links", []):
            normalized = normalize_link(link)
            if normalized in seen:
                continue
            seen.add(normalized)
            urls_to_check.append(normalized)

    status_map = {}
    checked_urls = set(urls_to_check[:max_links_to_check])
    crawled_statuses = {
        normalize_url(result.get("final_url") or result["url"]): result.get("status_code")
        for result in results
    }

    for url in checked_urls:
        if url in crawled_statuses and crawled_statuses[url] is not None:
            status_map[url] = crawled_statuses[url]
        else:
            status_map[url] = check_link_status(url)

    for result in results:
        broken_links = []
        unverified_links = []

        for link in result.get("internal_links", []):
            normalized = normalize_link(link)
            if normalized not in checked_urls:
                unverified_links.append(normalized)
                continue

            status = status_map.get(normalized)
            if status is None:
                unverified_links.append(normalized)
            elif status >= 400:
                broken_links.append(normalized)

        if broken_links:
            samples = broken_links[:5]
            message = f"Broken internal links found ({len(broken_links)}): {', '.join(samples)}"
            result["issues"].append(
                message
            )
            result["issue_codes"].append(ISSUE_BROKEN_INTERNAL_LINKS)
            result.setdefault("technical", {})["broken_internal_links_count"] = len(broken_links)
            result["technical"]["broken_internal_link_samples"] = samples
            result["technical"].setdefault("issues", []).append(
                build_issue(ISSUE_BROKEN_INTERNAL_LINKS, message)
            )

        if unverified_links:
            samples = unverified_links[:5]
            message = (
                f"Internal links could not be verified ({len(unverified_links)}): "
                f"{', '.join(samples)}"
            )
            result.setdefault("technical", {})["unverified_internal_links_count"] = len(
                unverified_links
            )
            result["technical"]["unverified_internal_link_samples"] = samples
            result["technical"].setdefault("issues", []).append(
                build_issue(ISSUE_UNVERIFIED_INTERNAL_LINKS, message)
            )


def dedupe_issues(results):
    for result in results:
        issue_pairs = []
        seen = set()

        for code, message in zip(result.get("issue_codes", []), result.get("issues", [])):
            pair = (code, message)
            if pair in seen:
                continue
            seen.add(pair)
            issue_pairs.append(pair)

        result["issue_codes"] = [code for code, _ in issue_pairs]
        result["issues"] = [message for _, message in issue_pairs]


def enrich_results_with_sitewide_checks(results):
    append_duplicate_metadata_issues(results)
    append_broken_internal_link_issues(results)
    dedupe_issues(results)
    return results
