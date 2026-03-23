import requests
from bs4 import BeautifulSoup


def classify_sitemap(sitemap_url):
    sitemap_url = sitemap_url.lower()

    if "tag" in sitemap_url:
        return "Tag"
    if "category" in sitemap_url:
        return "Category"
    if "author" in sitemap_url:
        return "Author"
    if "post" in sitemap_url:
        return "Post"
    if "page" in sitemap_url:
        return "Page"
    return "Other"


def count_urls_in_sitemap(sitemap_url):
    try:
        response = requests.get(
            sitemap_url,
            headers={"User-Agent": "SEO-Audit-App/1.0"},
            timeout=15
        )

        if response.status_code != 200:
            return 0

        soup = BeautifulSoup(response.text, "xml")
        return len(soup.find_all("url"))

    except requests.exceptions.RequestException:
        return 0


def sitemap_index_summary(sitemap_index_url):
    try:
        response = requests.get(
            sitemap_index_url,
            headers={"User-Agent": "SEO-Audit-App/1.0"},
            timeout=15
        )

        if response.status_code != 200:
            print("❌ Unable to fetch sitemap index")
            return []

        soup = BeautifulSoup(response.text, "xml")
        summary = []

        for sitemap in soup.find_all("sitemap"):
            loc = sitemap.find("loc").text.strip()
            lastmod = sitemap.find("lastmod")

            
            url_count = count_urls_in_sitemap(loc)
            sitemap_type = classify_sitemap(loc)
            
            summary.append({
                "sitemap": loc,
                "type": sitemap_type,
                "url_count": url_count,
                "last_modified": lastmod.text if lastmod else None
            })

        return summary

    except requests.exceptions.RequestException:
        return []

def detect_index_bloat(summary):
    total_urls = sum(s["url_count"] for s in summary)
    low_value_urls = sum(
        s["url_count"]
        for s in summary
        if s["type"] in ["Tag", "Category", "Author"]
    )

    if total_urls == 0:
        return None

    ratio = (low_value_urls / total_urls) * 100

    if ratio > 50:
        return f"🚨 Index Bloat Risk: {ratio:.1f}% of sitemap URLs are low-value (tags/categories/authors)"
    elif ratio > 30:
        return f"⚠️ Potential Index Bloat: {ratio:.1f}% low-value URLs"
    else:
        return "✅ No significant index bloat detected"
