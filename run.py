from crawler.sitemap_crawler import crawl_from_sitemap
from reports.excel_report import export_to_excel
from reports.sitemap_summary import sitemap_index_summary, detect_index_bloat
from rules.orphan_pages import find_orphan_pages
from rules.scoring import calculate_page_score

if __name__ == "__main__":

    SITE_URL = "https://www.togrowmarketing.com"
    SITEMAP_INDEX_URL = "https://www.togrowmarketing.com/sitemap_index.xml"

    print("\n========== SITEMAP ANALYSIS ==========")

    sitemap_summary = sitemap_index_summary(SITEMAP_INDEX_URL)

    if sitemap_summary:
        bloat_message = detect_index_bloat(sitemap_summary)
        print(bloat_message)
    else:
        print("⚠️ No sitemap summary available")

    print("\n========== STARTING SITEMAP CRAWL ==========")

    # Crawl pages + collect internal links
    results, internal_links = crawl_from_sitemap(
        SITE_URL,
        max_pages=50   # keep this small while testing
    )

    print("\n========== SITE AUDIT SUMMARY ==========")
    print(f"Total pages crawled: {len(results)}")
    print(f"Total internal links collected: {len(internal_links)}")

    # Extract sitemap URLs from crawl results
    sitemap_urls = [r["url"] for r in results]

    # Detect orphan pages
    orphan_pages = find_orphan_pages(sitemap_urls, internal_links)

    print("\n========== ORPHAN PAGE ANALYSIS ==========")
    print(f"Total orphan pages found: {len(orphan_pages)}")

    for url in orphan_pages[:10]:
        print(url)

    # --- SCORING ---
    print("\n========== PAGE SCORING ==========")

    for page in results:
        is_orphan = page["url"].rstrip("/") in [o.rstrip("/") for o in orphan_pages]
        score = calculate_page_score(page, is_orphan)
        page["seo_score"] = score

        print(f"{page['url']} -> Score: {score}")

    site_score = sum(p["seo_score"] for p in results) / len(results)
    print(f"\nOverall Site SEO Score: {round(site_score, 2)}")


    # --- FOOTPRINT ---
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
    
    # --- BASIC SCHEMA COVERAGE ---
    total_pages = len(results)
    pages_with_schema = sum(1 for r in results if r["footprint"]["schema_present"])

    coverage = (pages_with_schema / total_pages) * 100
    print(f"\nSchema Coverage: {round(coverage, 2)}%")


    # --- SMART SCHEMA COVERAGE (NEW LOGIC) ---
    blog_pages = [r for r in results if "/blog" in r["url"] or "how-" in r["url"]]

    correct_schema_pages = [
    r for r in blog_pages
    if "Article" in r["footprint"]["schema_types"]
   ]

if blog_pages:
    blog_schema_coverage = (len(correct_schema_pages) / len(blog_pages)) * 100
    print(f"Blog Article Schema Coverage: {round(blog_schema_coverage, 2)}%")
  
    # --- SCHEMA GAP DETECTION ---
# --- SCHEMA INTENT GAP DETECTION ---
print("\n========== SCHEMA INTENT GAP DETECTION ==========")

schema_gaps = []

for r in results:
    url = r["url"]
    schema_types = r["footprint"]["schema_types"]

    expected_schema = None

    # --- Intent Detection ---
    if "service" in url:
        expected_schema = "Service"

    elif "testimonial" in url or "review" in url:
        expected_schema = "Review"

    elif "team" in url or "about" in url:
        expected_schema = "Person"

    elif any(x in url for x in ["how-", "guide", "tips", "ideas"]) and "/blog/" not in url:
        expected_schema = "Article"

    # --- Validate ---
    if expected_schema and expected_schema not in schema_types:
        schema_gaps.append({
            "url": url,
            "expected": expected_schema,
            "found": schema_types
        })


print(f"\nTotal Schema Intent Issues: {len(schema_gaps)}")

for gap in schema_gaps[:5]:
    print(f"⚠ {gap['url']}")
    print(f"   Expected: {gap['expected']}")
    print(f"   Found: {gap['found']}")
    
# Export everything to Excel
excel_file = export_to_excel(results, orphan_pages, schema_gaps)

print(f"\n✅ SEO audit exported successfully: {excel_file}")
    
