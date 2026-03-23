from bs4 import BeautifulSoup
import json


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
        "hreflang_present": False,
        "open_graph_present": False,
        "cms_detected": None
    }

    # --- Canonical ---
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        footprint["canonical_present"] = True
        footprint["canonical_url"] = canonical.get("href")

    # --- Advanced Schema Detection ---
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
            if not script.string:
                continue

            data = json.loads(script.string)
            extracted = extract_types(data)

            if extracted:
                schema_types.extend(extracted)
                schema_count += 1

        except Exception:
            continue

    footprint["schema_types"] = list(set(schema_types))
    footprint["schema_count"] = schema_count
    footprint["schema_present"] = schema_count > 0

    # --- Schema Quality Score ---
    schema_score = 0

    if footprint["schema_present"]:
        schema_score += 5

    important_types = ["Organization", "Article", "Product", "BreadcrumbList"]

    for t in footprint["schema_types"]:
        if t in important_types:
            schema_score += 5

    footprint["schema_score"] = min(schema_score, 20)

    # --- Google Analytics ---
    if "gtag(" in html or "G-" in html:
        footprint["ga_detected"] = True

    # --- Google Tag Manager ---
    if "googletagmanager.com" in html or "GTM-" in html:
        footprint["gtm_detected"] = True

    # --- Facebook Pixel ---
    if "fbq(" in html or "connect.facebook.net" in html:
        footprint["facebook_pixel"] = True

    # --- Robots Meta ---
    robots = soup.find("meta", attrs={"name": "robots"})
    if robots and "noindex" in robots.get("content", "").lower():
        footprint["robots_noindex"] = True

    # --- Hreflang ---
    if soup.find("link", rel="alternate", hreflang=True):
        footprint["hreflang_present"] = True

    # --- Open Graph ---
    if soup.find("meta", property="og:title"):
        footprint["open_graph_present"] = True

    # --- Basic CMS Detection ---
    if "wp-content" in html:
        footprint["cms_detected"] = "WordPress"
    elif "shopify" in html.lower():
        footprint["cms_detected"] = "Shopify"

    return footprint