from bs4 import BeautifulSoup

def check_canonical(html, url):
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("link", rel="canonical")

    if not tag:
        return {"status": "missing"}

    canonical_url = tag.get("href")

    if canonical_url == url:
        return {"status": "self"}
    else:
        return {"status": "custom", "canonical": canonical_url}