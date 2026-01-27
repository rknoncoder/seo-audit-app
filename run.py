from crawler.site_crawler import crawl_site

if __name__ == "__main__":
    start_url = "https://togrowmarketing.com"

    results = crawl_site(start_url, max_pages=10)

    print("\n========== SITE AUDIT SUMMARY ==========")
    print(f"Total pages crawled: {len(results)}")

    missing_h1 = 0
    long_titles = 0
    zero_internal_links = 0

    for page in results:
        if "❌ Missing H1 tag" in page["issues"]:
            missing_h1 += 1

        for issue in page["issues"]:
            if "Title too long" in issue:
                long_titles += 1

        if page["internal_links_count"] == 0:
            zero_internal_links += 1

    print(f"Pages missing H1: {missing_h1}")
    print(f"Pages with long titles: {long_titles}")
    print(f"Pages with zero internal links: {zero_internal_links}")

    print("\n========== PAGE LEVEL ISSUES ==========")
    for page in results:
        if page["issues"]:
            print(f"\n{page['url']}")
            for issue in page["issues"]:
                print(issue)
