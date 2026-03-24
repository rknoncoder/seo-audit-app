from bs4 import BeautifulSoup


def clean_text(value):
    if value is None:
        return None

    text = value.strip()
    return text or None


def find_meta_description(soup):
    for tag in soup.find_all("meta"):
        name = (tag.get("name") or "").strip().lower()
        if name != "description":
            continue

        content = clean_text(tag.get("content"))
        if content:
            return content

    return None


def extract_h1s(soup):
    h1s = []
    for tag in soup.find_all("h1"):
        text = clean_text(tag.get_text(" ", strip=True))
        if text:
            h1s.append(text)
    return h1s


def extract_image_stats(soup):
    images = soup.find_all("img")
    missing_alt = 0

    for image in images:
        alt_text = image.get("alt")
        if alt_text is None or not alt_text.strip():
            missing_alt += 1

    return {
        "image_count": len(images),
        "images_missing_alt": missing_alt,
        "images_with_alt": max(len(images) - missing_alt, 0),
    }


def parse_basic_seo(html):
    soup = BeautifulSoup(html or "", "lxml")

    title = None
    if soup.title:
        title = clean_text(soup.title.get_text(" ", strip=True))

    meta_description = find_meta_description(soup)
    h1s = extract_h1s(soup)
    image_stats = extract_image_stats(soup)

    return {
        "title": title,
        "meta_description": meta_description,
        "h1": h1s[0] if h1s else None,
        "h1_count": len(h1s),
        "h1s": h1s,
        "image_count": image_stats["image_count"],
        "images_missing_alt": image_stats["images_missing_alt"],
        "images_with_alt": image_stats["images_with_alt"],
    }
