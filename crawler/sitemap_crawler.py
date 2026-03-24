from crawler.fetcher import fetch_page
from crawler.footprint import analyze_footprint
from crawler.links import extract_links
from crawler.parser import parse_basic_seo
from crawler.sitemap import fetch_sitemap_urls
from rules.seo_rules import run_seo_audit
from rules.technical import (
    build_robots_blocked_result,
    enrich_results_with_sitewide_checks,
    evaluate_technical_seo,
    is_allowed_by_robots,
    load_robots_rules,
)


def is_valid_page(url):
    exclude = [
        "/tag/",
        "/category/",
        "/author/",
        "/page/",
        "/feed/",
        "/wp-json/",
    ]
    return not any(x in url.lower() for x in exclude)


def crawl_from_sitemap(site_url, sitemap_url=None, max_pages=50):
    urls = fetch_sitemap_urls(site_url=site_url, sitemap_url=sitemap_url)

    if not urls:
        print("No URLs found in sitemap.")
        return [], set()

    results = []
    all_internal_links = set()
    filtered_urls = [url for url in urls if is_valid_page(url)]
    robots_rules = load_robots_rules(site_url)

    for url in filtered_urls[:max_pages]:
        print(f"Crawling: {url}")

        if not is_allowed_by_robots(robots_rules, url):
            footprint = analyze_footprint("")
            technical = build_robots_blocked_result(url, footprint, robots_rules)
            results.append(
                {
                    "url": url,
                    "final_url": url,
                    "status_code": None,
                    "seo_data": parse_basic_seo(""),
                    "issues": [issue["message"] for issue in technical["issues"]],
                    "issue_codes": [issue["code"] for issue in technical["issues"]],
                    "internal_links": [],
                    "internal_links_count": 0,
                    "external_links_count": 0,
                    "footprint": footprint,
                    "technical": technical,
                }
            )
            continue

        page = fetch_page(url)
        if not page.get("html"):
            continue

        seo_data = parse_basic_seo(page["html"])
        footprint = analyze_footprint(page["html"])
        seo_issues = run_seo_audit(seo_data)
        technical = evaluate_technical_seo(url, page, footprint)
        technical_issues = technical["issues"]
        all_issues = seo_issues + technical_issues
        links = extract_links(page["html"], page.get("final_url") or url)

        for link in links["internal_links"]:
            all_internal_links.add(link.rstrip("/"))

        results.append(
            {
                "url": url,
                "final_url": technical["final_url"],
                "status_code": page["status_code"],
                "seo_data": seo_data,
                "issues": [issue["message"] for issue in all_issues],
                "issue_codes": [issue["code"] for issue in all_issues],
                "internal_links": links["internal_links"],
                "internal_links_count": links["internal_count"],
                "external_links_count": links["external_count"],
                "footprint": footprint,
                "technical": technical,
            }
        )

    enrich_results_with_sitewide_checks(results)
    return results, all_internal_links
