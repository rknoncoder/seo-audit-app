from crawler.fetcher import fetch_page
from crawler.footprint import analyze_footprint
from crawler.links import extract_links
from crawler.parser import parse_basic_seo
from rules.seo_rules import run_seo_audit
from rules.technical import (
    build_robots_blocked_result,
    enrich_results_with_sitewide_checks,
    evaluate_technical_seo,
    is_allowed_by_robots,
    load_robots_rules,
)


def crawl_site(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    results = []
    robots_rules = load_robots_rules(start_url)

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")
        visited.add(current_url)

        if not is_allowed_by_robots(robots_rules, current_url):
            footprint = analyze_footprint("")
            technical = build_robots_blocked_result(current_url, footprint, robots_rules)
            results.append(
                {
                    "url": current_url,
                    "final_url": current_url,
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

        page = fetch_page(current_url)
        if not page.get("html"):
            continue

        seo_data = parse_basic_seo(page["html"])
        footprint = analyze_footprint(page["html"])
        seo_issues = run_seo_audit(seo_data)
        technical = evaluate_technical_seo(current_url, page, footprint)
        technical_issues = technical["issues"]
        all_issues = seo_issues + technical_issues
        links = extract_links(page["html"], page.get("final_url") or current_url)

        results.append(
            {
                "url": current_url,
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

        for link in links["internal_links"]:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    enrich_results_with_sitewide_checks(results)
    return results
