import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


HEADERS = {"User-Agent": "SEO-Audit-App/1.0"}


def possible_sitemap_urls(site_url):
    """
    Generate possible sitemap locations.
    """
    parsed = urlparse(site_url)
    domain = parsed.netloc.replace("www.", "")

    return [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap_index.xml",
    ]


def fetch_sitemap_document(sitemap_url, timeout=15):
    try:
        response = requests.get(sitemap_url, headers=HEADERS, timeout=timeout)
        if response.status_code != 200:
            return None
        return BeautifulSoup(response.text, "xml")
    except requests.exceptions.RequestException:
        return None


def extract_url_entries(soup):
    urls = []
    for url in soup.find_all("url"):
        loc = url.find("loc")
        if loc and loc.text:
            urls.append(loc.text.strip())
    return urls


def fetch_child_sitemap(sitemap_url):
    print(f"   Fetching child sitemap: {sitemap_url}")

    soup = fetch_sitemap_document(sitemap_url, timeout=8)
    if not soup:
        return []

    return extract_url_entries(soup)


def fetch_sitemap_urls(site_url=None, sitemap_url=None):
    sitemap_candidates = []

    if sitemap_url:
        sitemap_candidates.append(sitemap_url)

    if site_url:
        for candidate in possible_sitemap_urls(site_url):
            if candidate not in sitemap_candidates:
                sitemap_candidates.append(candidate)

    all_urls = []

    for candidate in sitemap_candidates:
        soup = fetch_sitemap_document(candidate)
        if not soup:
            continue

        print(f"Sitemap found: {candidate}")

        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            for sitemap in sitemap_tags:
                loc = sitemap.find("loc")
                if loc and loc.text:
                    all_urls.extend(fetch_child_sitemap(loc.text.strip()))
            if all_urls:
                return list(set(all_urls))
            continue

        all_urls.extend(extract_url_entries(soup))
        if all_urls:
            return list(set(all_urls))

    print("No valid sitemap found.")
    return []
