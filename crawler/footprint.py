import json

from bs4 import BeautifulSoup


def analyze_footprint(html):
    soup = BeautifulSoup(html, "lxml")

    footprint = {
        "canonical_present": False,
        "canonical_url": None,
        "schema_types": [],
        "schema_count": 0,
        "schema_present": False,
        "schema_score": 0,
        "ga_detected": False,
        "gtm_detected": False,
        "facebook_pixel": False,
        "robots_noindex": False,
        "robots_nofollow": False,
        "robots_meta_content": None,
        "hreflang_present": False,
        "open_graph_present": False,
        "cms_detected": None,
    }

    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        footprint["canonical_present"] = True
        footprint["canonical_url"] = canonical.get("href").strip()

    scripts = soup.find_all("script", type="application/ld+json")
    schema_types = []
    schema_count = 0

    def extract_types(obj):
        types = []

        if isinstance(obj, dict):
            if "@type" in obj:
                if isinstance(obj["@type"], list):
                    types.extend(obj["@type"])
                else:
                    types.append(obj["@type"])

            if "@graph" in obj:
                for item in obj["@graph"]:
                    types.extend(extract_types(item))

            for value in obj.values():
                types.extend(extract_types(value))

        elif isinstance(obj, list):
            for item in obj:
                types.extend(extract_types(item))

        return types

    for script in scripts:
        try:
            raw_value = script.string or script.get_text()
            if not raw_value:
                continue

            data = json.loads(raw_value)
            extracted = extract_types(data)

            if extracted:
                schema_types.extend(extracted)
                schema_count += 1

        except Exception:
            continue

    footprint["schema_types"] = sorted(set(schema_types))
    footprint["schema_count"] = schema_count
    footprint["schema_present"] = schema_count > 0

    schema_score = 0
    if footprint["schema_present"]:
        schema_score += 5

    important_types = ["Organization", "Article", "Product", "BreadcrumbList"]
    for schema_type in footprint["schema_types"]:
        if schema_type in important_types:
            schema_score += 5

    footprint["schema_score"] = min(schema_score, 20)

    if "gtag(" in html or "G-" in html:
        footprint["ga_detected"] = True

    if "googletagmanager.com" in html or "GTM-" in html:
        footprint["gtm_detected"] = True

    if "fbq(" in html or "connect.facebook.net" in html:
        footprint["facebook_pixel"] = True

    robots = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
    if robots:
        robots_content = (robots.get("content") or "").strip()
        if robots_content:
            footprint["robots_meta_content"] = robots_content
            robots_tokens = {token.strip().lower() for token in robots_content.split(",")}
            footprint["robots_noindex"] = "noindex" in robots_tokens
            footprint["robots_nofollow"] = "nofollow" in robots_tokens

    if soup.find("link", rel="alternate", hreflang=True):
        footprint["hreflang_present"] = True

    if soup.find("meta", property="og:title"):
        footprint["open_graph_present"] = True

    if "wp-content" in html:
        footprint["cms_detected"] = "WordPress"
    elif "shopify" in html.lower():
        footprint["cms_detected"] = "Shopify"

    return footprint
