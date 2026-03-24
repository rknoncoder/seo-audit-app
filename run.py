import argparse

from crawler.sitemap_crawler import crawl_from_sitemap
from reports.excel_report import export_to_excel
from reports.sitemap_summary import detect_index_bloat, sitemap_index_summary
from rules.orphan_pages import find_orphan_pages
from rules.scoring import calculate_page_score
from rules.seo_rules import (
    ISSUE_DUPLICATE_META_DESCRIPTION,
    ISSUE_DUPLICATE_TITLE,
    ISSUE_MISSING_IMAGE_ALT,
    ISSUE_MULTIPLE_H1,
)
from rules.technical import (
    ISSUE_BLOCKED_BY_ROBOTS,
    ISSUE_BROKEN_INTERNAL_LINKS,
    ISSUE_CANONICAL_MISSING,
    ISSUE_META_NOINDEX,
    ISSUE_REDIRECTED,
    ISSUE_UNVERIFIED_INTERNAL_LINKS,
    ISSUE_X_ROBOTS_NOINDEX,
)


DEFAULT_SITE_URL = "https://www.togrowmarketing.com"
DEFAULT_SITEMAP_URL = "https://www.togrowmarketing.com/sitemap_index.xml"
DEFAULT_MAX_PAGES = 100

AUDIT_MODE_PAGE_LIMITS = {
    "quick": 25,
    "standard": DEFAULT_MAX_PAGES,
    "deep": 250,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run an SEO audit from a sitemap.")
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL,
        help="Primary site URL used for crawl context and sitemap fallback discovery.",
    )
    parser.add_argument(
        "--sitemap-url",
        default=DEFAULT_SITEMAP_URL,
        help="Explicit sitemap or sitemap index URL to crawl first.",
    )
    parser.add_argument(
        "--mode",
        choices=sorted(AUDIT_MODE_PAGE_LIMITS.keys()),
        default="standard",
        help="Preset crawl depth. Use --max-pages to override the preset.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of sitemap URLs to crawl. Defaults to the selected mode limit.",
    )
    return parser.parse_args()


def resolve_max_pages(mode, max_pages):
    if max_pages is not None:
        return max(1, max_pages)
    return AUDIT_MODE_PAGE_LIMITS[mode]


def detect_schema_gaps(results):
    schema_gaps = []

    for page in results:
        url = page["url"]
        schema_types = page["footprint"]["schema_types"]
        expected_schema = None

        if "service" in url:
            expected_schema = "Service"
        elif "testimonial" in url or "review" in url:
            expected_schema = "Review"
        elif "team" in url or "about" in url:
            expected_schema = "Person"
        elif any(x in url for x in ["how-", "guide", "tips", "ideas"]) and "/blog/" not in url:
            expected_schema = "Article"

        if expected_schema and expected_schema not in schema_types:
            schema_gaps.append(
                {
                    "url": url,
                    "expected": expected_schema,
                    "found": schema_types,
                }
            )

    return schema_gaps


def main():
    args = parse_args()
    site_url = args.site_url
    sitemap_url = args.sitemap_url
    max_pages = resolve_max_pages(args.mode, args.max_pages)

    print("\n========== AUDIT SETTINGS ==========")
    print(f"Mode: {args.mode}")
    print(f"Site URL: {site_url}")
    print(f"Sitemap URL: {sitemap_url}")
    print(f"Max pages: {max_pages}")

    print("\n========== SITEMAP ANALYSIS ==========")

    sitemap_summary = sitemap_index_summary(sitemap_url)

    if sitemap_summary:
        bloat_message = detect_index_bloat(sitemap_summary)
        print(bloat_message)
    else:
        print("No sitemap summary available")

    print("\n========== STARTING SITEMAP CRAWL ==========")

    results, internal_links = crawl_from_sitemap(
        site_url,
        sitemap_url=sitemap_url,
        max_pages=max_pages,
    )

    print("\n========== SITE AUDIT SUMMARY ==========")
    print(f"Total pages crawled: {len(results)}")
    print(f"Total internal links collected: {len(internal_links)}")

    if not results:
        print("\nNo crawl results available. Skipping scoring, schema analysis, and export.")
        return

    sitemap_urls = [page["url"] for page in results]
    orphan_pages = find_orphan_pages(sitemap_urls, internal_links)

    print("\n========== ORPHAN PAGE ANALYSIS ==========")
    print(f"Total orphan pages found: {len(orphan_pages)}")

    for url in orphan_pages[:10]:
        print(url)

    print("\n========== PAGE SCORING ==========")

    normalized_orphans = {url.rstrip("/") for url in orphan_pages}

    for page in results:
        is_orphan = page["url"].rstrip("/") in normalized_orphans
        score = calculate_page_score(page, is_orphan)
        page["seo_score"] = score
        print(f"{page['url']} -> Score: {score}")

    site_score = sum(page["seo_score"] for page in results) / len(results)
    print(f"\nOverall Site SEO Score: {round(site_score, 2)}")

    print("\n========== FOOTPRINT SUMMARY ==========")

    for page in results[:5]:
        fp = page["footprint"]

        print(f"\n{page['url']}")
        print(f"Canonical: {fp['canonical_present']}")
        print(f"Schema Types: {fp['schema_types']}")
        print(f"GA Detected: {fp['ga_detected']}")
        print(f"GTM Detected: {fp['gtm_detected']}")
        print(f"Facebook Pixel: {fp['facebook_pixel']}")
        print(f"CMS: {fp['cms_detected']}")
        print(f"Schema Count: {fp['schema_count']}")
        print(f"Schema Score: {fp['schema_score']}")

    total_pages = len(results)
    pages_with_schema = sum(1 for page in results if page["footprint"]["schema_present"])
    coverage = (pages_with_schema / total_pages) * 100 if total_pages else 0
    print(f"\nSchema Coverage: {round(coverage, 2)}%")

    redirected_pages = sum(1 for page in results if ISSUE_REDIRECTED in page["issue_codes"])
    noindex_pages = sum(
        1
        for page in results
        if ISSUE_META_NOINDEX in page["issue_codes"]
        or ISSUE_X_ROBOTS_NOINDEX in page["issue_codes"]
    )
    missing_canonical_pages = sum(
        1 for page in results if ISSUE_CANONICAL_MISSING in page["issue_codes"]
    )
    duplicate_title_pages = sum(
        1 for page in results if ISSUE_DUPLICATE_TITLE in page["issue_codes"]
    )
    duplicate_meta_pages = sum(
        1
        for page in results
        if ISSUE_DUPLICATE_META_DESCRIPTION in page["issue_codes"]
    )
    multiple_h1_pages = sum(
        1 for page in results if ISSUE_MULTIPLE_H1 in page["issue_codes"]
    )
    missing_alt_pages = sum(
        1 for page in results if ISSUE_MISSING_IMAGE_ALT in page["issue_codes"]
    )
    robots_blocked_pages = sum(
        1 for page in results if ISSUE_BLOCKED_BY_ROBOTS in page["issue_codes"]
    )
    broken_internal_link_pages = sum(
        1 for page in results if ISSUE_BROKEN_INTERNAL_LINKS in page["issue_codes"]
    )
    unverified_internal_link_pages = sum(
        1
        for page in results
        if any(
            issue.get("code") == ISSUE_UNVERIFIED_INTERNAL_LINKS
            for issue in page.get("technical", {}).get("issues", [])
        )
    )

    print("\n========== TECHNICAL SEO SUMMARY ==========")
    print(f"Pages that redirected: {redirected_pages}")
    print(f"Pages marked noindex: {noindex_pages}")
    print(f"Pages missing canonical: {missing_canonical_pages}")
    print(f"Pages blocked by robots.txt: {robots_blocked_pages}")
    print(f"Pages with broken internal links: {broken_internal_link_pages}")
    print(f"Pages with unverified internal links: {unverified_internal_link_pages}")

    print("\n========== ON-PAGE SEO SUMMARY ==========")
    print(f"Pages with duplicate titles: {duplicate_title_pages}")
    print(f"Pages with duplicate meta descriptions: {duplicate_meta_pages}")
    print(f"Pages with multiple H1s: {multiple_h1_pages}")
    print(f"Pages with missing image alt text: {missing_alt_pages}")

    blog_pages = [page for page in results if "/blog" in page["url"] or "how-" in page["url"]]
    correct_schema_pages = [
        page for page in blog_pages if "Article" in page["footprint"]["schema_types"]
    ]

    if blog_pages:
        blog_schema_coverage = (len(correct_schema_pages) / len(blog_pages)) * 100
        print(f"Blog Article Schema Coverage: {round(blog_schema_coverage, 2)}%")
    else:
        print("Blog Article Schema Coverage: N/A")

    print("\n========== SCHEMA INTENT GAP DETECTION ==========")

    schema_gaps = detect_schema_gaps(results)

    print(f"\nTotal Schema Intent Issues: {len(schema_gaps)}")

    for gap in schema_gaps[:5]:
        print(f"Warning: {gap['url']}")
        print(f"   Expected: {gap['expected']}")
        print(f"   Found: {gap['found']}")

    excel_file = export_to_excel(results, orphan_pages, schema_gaps)
    print(f"\nSEO audit exported successfully: {excel_file}")


if __name__ == "__main__":
    main()
