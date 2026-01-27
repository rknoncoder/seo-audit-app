from bs4 import BeautifulSoup

def parse_basic_seo(html):
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title else None

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag else None

    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    return {
        "title": title,
        "meta_description": meta_description,
        "h1": h1
    }
