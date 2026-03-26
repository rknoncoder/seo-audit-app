from collections import defaultdict

import pandas as pd

from rules.seo_rules import (
    MISSING_H1,
    TITLE_TOO_LONG,
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


LOW_VALUE_PATTERNS = {
    "/tag/": "Tag",
    "/category/": "Category",
    "/author/": "Author",
    "/page/": "Pagination",
    "/feed/": "Feed",
    "/wp-json/": "WP JSON",
}


def add_orphan_sheet(writer, orphan_urls):
    if not orphan_urls:
        df = pd.DataFrame({"Message": ["No orphan pages detected"]})
    else:
        df = pd.DataFrame({"Orphan URL": orphan_urls})

    df.to_excel(writer, sheet_name="Orphan Pages", index=False)


def get_schema_recommendation(expected):
    recommendations = {
        "Service": "Add Service schema (JSON-LD) with name, description, provider, etc.",
        "Article": "Add Article schema with headline, author, datePublished, etc.",
        "Review": "Add Review schema with rating,author, itemReviewed, etc.",
        "Person": "Add Person schema with name, jobTitle, sameAs links, etc.",
    }
    return recommendations.get(expected, "Add appropriate structured data schema")


def classify_low_value_url(url):
    lower_url = url.lower()
    for pattern, label in LOW_VALUE_PATTERNS.items():
        if pattern in lower_url:
            return label
    return None


def build_low_value_urls_df(results):
    low_value_map = defaultdict(set)
    low_value_types = {}

    for result in results:
        source_url = result["url"]
        for link in result.get("internal_links", []):
            url_type = classify_low_value_url(link)
            if not url_type:
                continue
            low_value_map[link].add(source_url)
            low_value_types[link] = url_type

    if not low_value_map:
        return pd.DataFrame({"Message": ["No low-value internal URLs detected"]})

    rows = []
    for url in sorted(low_value_map):
        source_pages = sorted(low_value_map[url])
        rows.append(
            {
                "Low Value URL": url,
                "Type": low_value_types[url],
                "Linked From Page Count": len(source_pages),
                "Sample Source Pages": ", ".join(source_pages[:5]),
            }
        )

    return pd.DataFrame(rows)


def export_to_excel(results, orphan_pages, schema_gaps, filename="seo-audit.xlsx"):
    total_pages = len(results)
    missing_h1 = sum(1 for result in results if MISSING_H1 in result["issues"])
    long_titles = sum(
        1
        for result in results
        for issue in result["issues"]
        if issue.startswith(TITLE_TOO_LONG)
    )
    noindex_pages = sum(
        1
        for result in results
        if ISSUE_META_NOINDEX in result.get("issue_codes", [])
        or ISSUE_X_ROBOTS_NOINDEX in result.get("issue_codes", [])
    )
    missing_canonicals = sum(
        1 for result in results if ISSUE_CANONICAL_MISSING in result.get("issue_codes", [])
    )
    redirected_pages = sum(
        1 for result in results if ISSUE_REDIRECTED in result.get("issue_codes", [])
    )
    duplicate_titles = sum(
        1 for result in results if ISSUE_DUPLICATE_TITLE in result.get("issue_codes", [])
    )
    duplicate_meta = sum(
        1
        for result in results
        if ISSUE_DUPLICATE_META_DESCRIPTION in result.get("issue_codes", [])
    )
    multiple_h1 = sum(
        1 for result in results if ISSUE_MULTIPLE_H1 in result.get("issue_codes", [])
    )
    missing_alt = sum(
        1 for result in results if ISSUE_MISSING_IMAGE_ALT in result.get("issue_codes", [])
    )
    robots_blocked = sum(
        1 for result in results if ISSUE_BLOCKED_BY_ROBOTS in result.get("issue_codes", [])
    )
    broken_internal_links = sum(
        1 for result in results if ISSUE_BROKEN_INTERNAL_LINKS in result.get("issue_codes", [])
    )
    unverified_internal_links = sum(
        1
        for result in results
        if any(
            issue.get("code") == ISSUE_UNVERIFIED_INTERNAL_LINKS
            for issue in result.get("technical", {}).get("issues", [])
        )
    )
    low_value_urls_df = build_low_value_urls_df(results)
    low_value_url_count = (
        0
        if "Low Value URL" not in low_value_urls_df.columns
        else len(low_value_urls_df.index)
    )

    summary_df = pd.DataFrame(
        [
            {"Metric": "Total Pages Crawled", "Value": total_pages},
            {"Metric": "Pages Missing H1", "Value": missing_h1},
            {"Metric": "Pages With Long Titles", "Value": long_titles},
            {"Metric": "Pages Marked Noindex", "Value": noindex_pages},
            {"Metric": "Pages Missing Canonical", "Value": missing_canonicals},
            {"Metric": "Pages That Redirected", "Value": redirected_pages},
            {"Metric": "Pages With Duplicate Titles", "Value": duplicate_titles},
            {"Metric": "Pages With Duplicate Meta Descriptions", "Value": duplicate_meta},
            {"Metric": "Pages With Multiple H1s", "Value": multiple_h1},
            {"Metric": "Pages With Missing Image Alt Text", "Value": missing_alt},
            {"Metric": "Pages Blocked By robots.txt", "Value": robots_blocked},
            {"Metric": "Pages With Broken Internal Links", "Value": broken_internal_links},
            {"Metric": "Pages With Unverified Internal Links", "Value": unverified_internal_links},
            {"Metric": "Low Value Internal URLs Found", "Value": low_value_url_count},
        ]
    )

    page_rows = []
    technical_rows = []

    for result in results:
        technical = result.get("technical", {})
        seo_data = result["seo_data"]

        page_rows.append(
            {
                "URL": result["url"],
                "Final URL": result.get("final_url"),
                "SEO Score": result.get("seo_score", "N/A"),
                "Status Code": result["status_code"],
                "Title": seo_data.get("title"),
                "Meta Description": seo_data.get("meta_description"),
                "H1": seo_data.get("h1"),
                "H1 Count": seo_data.get("h1_count"),
                "Image Count": seo_data.get("image_count"),
                "Images Missing Alt": seo_data.get("images_missing_alt"),
                "Issues": " | ".join(result["issues"]) if result["issues"] else "No issues",
            }
        )

        technical_rows.append(
            {
                "URL": result["url"],
                "Final URL": technical.get("final_url"),
                "Indexable": technical.get("indexable"),
                "Robots Allowed": technical.get("robots_allowed"),
                "Redirected": technical.get("redirected"),
                "Redirect Count": technical.get("redirect_count"),
                "Canonical Status": technical.get("canonical_status"),
                "Canonical URL": technical.get("canonical_url"),
                "Meta Robots": technical.get("meta_robots"),
                "X-Robots-Tag": technical.get("x_robots_tag"),
                "Broken Internal Link Count": technical.get("broken_internal_links_count"),
                "Broken Internal Link Samples": ", ".join(
                    technical.get("broken_internal_link_samples", [])
                ),
                "Unverified Internal Link Count": technical.get("unverified_internal_links_count"),
                "Unverified Internal Link Samples": ", ".join(
                    technical.get("unverified_internal_link_samples", [])
                ),
                "Technical Issues": " | ".join(
                    issue["message"] for issue in technical.get("issues", [])
                )
                or "No issues",
            }
        )

    pages_df = pd.DataFrame(page_rows)
    technical_df = pd.DataFrame(technical_rows)

    links_df = pd.DataFrame(
        [
            {
                "URL": result["url"],
                "Internal Links": result["internal_links_count"],
                "External Links": result["external_links_count"],
            }
            for result in results
        ]
    )

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        pages_df.to_excel(writer, sheet_name="Page Audit", index=False)
        technical_df.to_excel(writer, sheet_name="Technical SEO", index=False)
        links_df.to_excel(writer, sheet_name="Links", index=False)
        low_value_urls_df.to_excel(writer, sheet_name="Low Value URLs", index=False)
        add_orphan_sheet(writer, orphan_pages)

        if schema_gaps:
            schema_df = pd.DataFrame(
                [
                    {
                        "URL": gap["url"],
                        "Expected Schema": gap["expected"],
                        "Found Schemas": ", ".join(gap["found"]),
                        "Recommendation": get_schema_recommendation(gap["expected"]),
                    }
                    for gap in schema_gaps
                ]
            )
        else:
            schema_df = pd.DataFrame({"Message": ["No schema gaps detected"]})

        schema_df.to_excel(writer, sheet_name="Schema Gaps", index=False)

    return filename
