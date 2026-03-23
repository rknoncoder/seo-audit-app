import math

def calculate_page_score(page_data, is_orphan):
    score = 100

    issues = page_data["issues"]
    internal_links = page_data["internal_links_count"]
    url = page_data["url"]

    # --- Page Type Weight ---
    if "/service" in url:
        importance_weight = 1.2
    elif "/blog" in url or "/post" in url:
        importance_weight = 1.0
    else:
        importance_weight = 0.9

    # --- Structural Issues ---
    for issue in issues:
        if "Missing H1" in issue:
            score -= 20
        elif "Title too long" in issue:
            score -= 8
        elif "Meta description too long" in issue:
            score -= 5

    # --- Internal Link Strength ---
    if internal_links == 0:
        score -= 18
    else:
        score += min(math.log(internal_links + 1) * 2, 8)

    # --- Orphan Penalty ---
    if is_orphan:
        score -= 25

    score *= importance_weight

    return round(max(min(score, 100), 0), 2)