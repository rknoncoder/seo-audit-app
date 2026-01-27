from crawler.site_crawler import crawl_site
from reports.excel_report import export_to_excel

if __name__ == "__main__":
    start_url = "https://togrowmarketing.com"

    results = crawl_site(start_url, max_pages=10)

    print("\n========== SITE AUDIT SUMMARY ==========")
    print(f"Total pages crawled: {len(results)}")

    excel_file = export_to_excel(results)
    print(f"\n✅ SEO audit exported to: {excel_file}")
