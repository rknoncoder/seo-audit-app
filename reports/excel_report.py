import pandas as pd


def add_orphan_sheet(writer, orphan_urls):
    """
    Adds a sheet listing orphan pages
    """
    if not orphan_urls:
        df = pd.DataFrame({"Message": ["No orphan pages detected"]})
    else:
        df = pd.DataFrame({
            "Orphan URL": orphan_urls
        })

    df.to_excel(writer, sheet_name="Orphan Pages", index=False)


def export_to_excel(results, orphan_pages, schema_gaps, filename="seo-audit.xlsx"):

    # ---------- SUMMARY ----------
    total_pages = len(results)
    missing_h1 = sum(1 for r in results if "❌ Missing H1 tag" in r["issues"])
    long_titles = sum(
        1
        for r in results
        for issue in r["issues"]
        if "Title too long" in issue
    )

    summary_df = pd.DataFrame([
        {"Metric": "Total Pages Crawled", "Value": total_pages},
        {"Metric": "Pages Missing H1", "Value": missing_h1},
        {"Metric": "Pages With Long Titles", "Value": long_titles},
    ])

    # ---------- PAGE LEVEL AUDIT ----------
    page_rows = []
    for r in results:
        page_rows.append({
            "URL": r["url"],
            "SEO Score": r.get("seo_score", "N/A"),
            "Status Code": r["status_code"],
            "Title": r["seo_data"]["title"],
            "Meta Description": r["seo_data"]["meta_description"],
            "H1": r["seo_data"]["h1"],
            "Issues": " | ".join(r["issues"]) if r["issues"] else "No issues",
        })

    pages_df = pd.DataFrame(page_rows)

    # ---------- LINK COUNTS ----------
    links_df = pd.DataFrame([
        {
            "URL": r["url"],
            "Internal Links": r["internal_links_count"],
            "External Links": r["external_links_count"],
        }
        for r in results
    ])

    # ---------- WRITE EXCEL ----------
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        pages_df.to_excel(writer, sheet_name="Page Audit", index=False)
        links_df.to_excel(writer, sheet_name="Links", index=False)
        add_orphan_sheet(writer, orphan_pages)
        
        if schema_gaps:
           schema_df = pd.DataFrame([
            {
                "URL": gap["url"],
                "Expected Schema": gap["expected"],
                "Found Schemas": ", ".join(gap["found"])
            }
            for gap in schema_gaps
        ])   
        else:
         schema_df = pd.DataFrame({"Message": ["No schema gaps detected"]})
        schema_df.to_excel(writer, sheet_name="Schema Gaps", index=False)     


    return filename
