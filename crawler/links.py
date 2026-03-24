from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


def normalize_domain(url):
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain.replace("www.", "", 1)
    return domain


def normalize_link(url):
    normalized, _ = urldefrag(url)
    parsed = urlparse(normalized)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    normalized_url = parsed._replace(scheme=scheme, netloc=netloc, path=path, fragment="")
    return normalized_url.geturl()


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

        full_url = normalize_link(urljoin(base_url, href))
        link_domain = normalize_domain(full_url)

        if link_domain == base_domain:
            internal_links.add(full_url)
        else:
            external_links.add(full_url)

    return {
        "internal_links": sorted(internal_links),
        "external_links": sorted(external_links),
        "internal_count": len(internal_links),
        "external_count": len(external_links),
    }
