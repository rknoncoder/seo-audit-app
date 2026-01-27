from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def normalize_domain(url):
    """
    Convert:
    - https://www.example.com
    - http://example.com
    into: example.com
    """
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain.replace("www.", "", 1)
    return domain


def extract_links(html, base_url):
    soup = BeautifulSoup(html, "lxml")

    internal_links = set()
    external_links = set()

    base_domain = normalize_domain(base_url)

    for link in soup.find_all("a", href=True):
        href = link.get("href").strip()

        if (
            href.startswith("#")
            or href.startswith("javascript")
            or href.startswith("mailto:")
            or href.startswith("tel:")
        ):
            continue

        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)

        link_domain = normalize_domain(full_url)

        if link_domain == base_domain:
            internal_links.add(full_url)
        else:
            external_links.add(full_url)

    return {
        "internal_links": list(internal_links),
        "external_links": list(external_links),
        "internal_count": len(internal_links),
        "external_count": len(external_links),
    }
