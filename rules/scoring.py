import math
from urllib.parse import urlparse

from rules.seo_rules import (
    ISSUE_DUPLICATE_META_DESCRIPTION,
    ISSUE_DUPLICATE_TITLE,
    ISSUE_META_DESCRIPTION_TOO_LONG,
    ISSUE_MISSING_H1,
    ISSUE_MISSING_IMAGE_ALT,
    ISSUE_MISSING_META_DESCRIPTION,
    ISSUE_MISSING_TITLE,
    ISSUE_MULTIPLE_H1,
    ISSUE_TITLE_TOO_LONG,
)
from rules.technical import (
    ISSUE_BLOCKED_BY_ROBOTS,
    ISSUE_BROKEN_INTERNAL_LINKS,
    ISSUE_CANONICAL_DIFFERENT,
    ISSUE_CANONICAL_MISSING,
    ISSUE_META_NOINDEX,
    ISSUE_NON_200_STATUS,
    ISSUE_REDIRECTED,
    ISSUE_X_ROBOTS_NOINDEX,
)


ISSUE_PENALTIES = {
    ISSUE_MISSING_TITLE: 20,
    ISSUE_TITLE_TOO_LONG: 8,
    ISSUE_MISSING_META_DESCRIPTION: 10,
    ISSUE_META_DESCRIPTION_TOO_LONG: 5,
    ISSUE_MISSING_H1: 20,
    ISSUE_MULTIPLE_H1: 8,
    ISSUE_MISSING_IMAGE_ALT: 6,
    ISSUE_DUPLICATE_TITLE: 12,
    ISSUE_DUPLICATE_META_DESCRIPTION: 10,
    ISSUE_CANONICAL_MISSING: 10,
    ISSUE_CANONICAL_DIFFERENT: 6,
    ISSUE_META_NOINDEX: 25,
    ISSUE_X_ROBOTS_NOINDEX: 25,
    ISSUE_REDIRECTED: 5,
    ISSUE_NON_200_STATUS: 30,
    ISSUE_BLOCKED_BY_ROBOTS: 30,
    ISSUE_BROKEN_INTERNAL_LINKS: 20,
}


def classify_page_type(url):
    path = urlparse(url).path.strip("/").lower()
    segments = [segment for segment in path.split("/") if segment]

    if not segments:
        return "homepage"

    segment_set = set(segments)

    if segment_set & {"contact", "pricing", "quote", "demo", "book", "services", "service"}:
        return "conversion"

    if segment_set & {"product", "products", "solutions", "location", "locations"}:
        return "commercial"

    if segment_set & {"blog", "post", "posts", "news", "article", "articles", "guides", "guide"}:
        return "content"

    if segment_set & {"privacy-policy", "privacy", "terms", "search", "feed", "author", "tag"}:
        return "utility"

    return "general"


def get_importance_weight(url):
    page_type = classify_page_type(url)

    weights = {
        "homepage": 1.1,
        "conversion": 1.1,
        "commercial": 1.05,
        "content": 1.0,
        "general": 1.0,
        "utility": 0.9,
    }

    return weights.get(page_type, 1.0)


def calculate_page_score(page_data, is_orphan):
    score = 100

    issue_codes = set(page_data.get("issue_codes", []))
    internal_links = page_data["internal_links_count"]
    url = page_data["url"]

    for issue_code in issue_codes:
        score -= ISSUE_PENALTIES.get(issue_code, 0)

    if ISSUE_BLOCKED_BY_ROBOTS not in issue_codes:
        if internal_links == 0:
            score -= 18
        else:
            score += min(math.log(internal_links + 1) * 2, 8)

    if is_orphan:
        score -= 25

    score *= get_importance_weight(url)

    return round(max(min(score, 100), 0), 2)
