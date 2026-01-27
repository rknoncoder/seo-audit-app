from crawler.fetcher import fetch_page
from crawler.parser import parse_basic_seo
from rules.seo_rules import run_seo_checks

if __name__ == "__main__":
    url = "https://togrowmarketing.com"

    page = fetch_page(url)

    if page.get("html"):
        seo_data = parse_basic_seo(page["html"])
        issues = run_seo_checks(seo_data)

        print("\nURL:", page["url"])
        print("Status Code:", page["status_code"])

        print("\n--- SEO DATA ---")
        for key, value in seo_data.items():
            print(f"{key}: {value}")

        print("\n--- SEO ISSUES FOUND ---")
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ No issues found")

    else:
        print("Error:", page.get("error"))
