from crawler.fetcher import fetch_page
from crawler.parser import parse_basic_seo
from crawler.links import extract_links
from crawler.sitemap import fetch_sitemap_urls
from rules.seo_rules import run_seo_checks
from crawler.footprint import analyze_footprint


def is_valid_page(url):
    exclude = [
        "/tag/",
        "/category/",
        "/author/",
        "/page/",
        "/feed/",
        "/wp-json/"
    ]
    return not any(x in url.lower() for x in exclude)


def crawl_from_sitemap(site_url, max_pages=50):
    urls = fetch_sitemap_urls(site_url)

    if not urls:
        print("❌ No URLs found in sitemap.")
        return [], set()

    results = []
    all_internal_links = set()

    filtered_urls = [u for u in urls if is_valid_page(u)]

    for url in filtered_urls[:max_pages]:
        print(f"Crawling: {url}")

        page = fetch_page(url)
        if not page.get("html"):
            continue

        seo_data = parse_basic_seo(page["html"])
        issues = run_seo_checks(seo_data)
        links = extract_links(page["html"], url)
        footprint = analyze_footprint(page["html"])

        # collect internal links correctly
        for link in links["internal_links"]:
            all_internal_links.add(link.rstrip("/"))

        results.append({
            "url": url,
            "status_code": page["status_code"],
            "seo_data": seo_data,
            "issues": issues,
            "internal_links_count": links["internal_count"],
            "external_links_count": links["external_count"],
            "footprint": footprint,
        })

    return results, all_internal_links