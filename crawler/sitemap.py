import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def possible_sitemap_urls(site_url):
    """
    Generate possible sitemap locations
    """
    parsed = urlparse(site_url)
    domain = parsed.netloc.replace("www.", "")

    return [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap_index.xml",
    ]


def fetch_sitemap_urls(site_url):
    sitemap_urls = possible_sitemap_urls(site_url)
    all_urls = []

    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(
                sitemap_url,
                headers={"User-Agent": "SEO-Audit-App/1.0"},
                timeout=15
            )

            if response.status_code != 200:
                continue

            print(f"✔ Sitemap found: {sitemap_url}")

            soup = BeautifulSoup(response.text, "xml")

            # Case 1: Sitemap Index
            sitemap_tags = soup.find_all("sitemap")
            if sitemap_tags:
                for sitemap in sitemap_tags:
                    loc = sitemap.find("loc")
                    if loc:
                        all_urls.extend(fetch_child_sitemap(loc.text.strip()))
                return list(set(all_urls))

            # Case 2: Regular Sitemap
            url_tags = soup.find_all("url")
            for url in url_tags:
                loc = url.find("loc")
                if loc:
                    all_urls.append(loc.text.strip())

            if all_urls:
                return list(set(all_urls))

        except requests.exceptions.RequestException:
            continue

    print("❌ No valid sitemap found.")
    return []


def fetch_child_sitemap(sitemap_url, max_pages=5):
    urls = []
    page = 1

    while page <= max_pages:
        paged_url = sitemap_url if page == 1 else f"{sitemap_url}?page={page}"
        print(f"   ↳ Fetching: {paged_url}")

        try:
            response = requests.get(
                paged_url,
                headers={"User-Agent": "SEO-Audit-App/1.0"},
                timeout=8
            )

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, "xml")
            url_tags = soup.find_all("url")

            if not url_tags:
                break

            for url in url_tags:
                loc = url.find("loc")
                if loc:
                    urls.append(loc.text.strip())

            page += 1

        except requests.exceptions.RequestException:
            break

    return urls
