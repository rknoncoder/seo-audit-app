from crawler.fetcher import fetch_page
from crawler.parser import parse_basic_seo
from crawler.links import extract_links
from rules.seo_rules import run_seo_checks


def crawl_site(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    results = []

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")

        page = fetch_page(current_url)
        visited.add(current_url)

        if not page.get("html"):
            continue

        seo_data = parse_basic_seo(page["html"])
        issues = run_seo_checks(seo_data)
        links = extract_links(page["html"], current_url)

        results.append({
            "url": current_url,
            "status_code": page["status_code"],
            "seo_data": seo_data,
            "issues": issues,
            "internal_links_count": links["internal_count"],
            "external_links_count": links["external_count"],
        })

        # Queue new internal links
        for link in links["internal_links"]:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    return results
