MISSING_TITLE = "Missing title tag"
TITLE_TOO_LONG = "Title too long"
MISSING_META_DESCRIPTION = "Missing meta description"
META_DESCRIPTION_TOO_LONG = "Meta description too long"
MISSING_H1 = "Missing H1 tag"
MULTIPLE_H1 = "Multiple H1 tags found"
MISSING_IMAGE_ALT = "Images missing alt text"
DUPLICATE_TITLE = "Duplicate title tag"
DUPLICATE_META_DESCRIPTION = "Duplicate meta description"

ISSUE_MISSING_TITLE = "missing_title"
ISSUE_TITLE_TOO_LONG = "title_too_long"
ISSUE_MISSING_META_DESCRIPTION = "missing_meta_description"
ISSUE_META_DESCRIPTION_TOO_LONG = "meta_description_too_long"
ISSUE_MISSING_H1 = "missing_h1"
ISSUE_MULTIPLE_H1 = "multiple_h1"
ISSUE_MISSING_IMAGE_ALT = "missing_image_alt"
ISSUE_DUPLICATE_TITLE = "duplicate_title"
ISSUE_DUPLICATE_META_DESCRIPTION = "duplicate_meta_description"


def build_issue(code, message):
    return {"code": code, "message": message}


def check_title(title):
    issues = []

    if not title:
        issues.append(build_issue(ISSUE_MISSING_TITLE, MISSING_TITLE))
    elif len(title) > 60:
        issues.append(
            build_issue(ISSUE_TITLE_TOO_LONG, f"{TITLE_TOO_LONG} ({len(title)} characters)")
        )

    return issues


def check_meta_description(meta_description):
    issues = []

    if not meta_description:
        issues.append(
            build_issue(ISSUE_MISSING_META_DESCRIPTION, MISSING_META_DESCRIPTION)
        )
    elif len(meta_description) > 160:
        issues.append(
            build_issue(
                ISSUE_META_DESCRIPTION_TOO_LONG,
                f"{META_DESCRIPTION_TOO_LONG} ({len(meta_description)} characters)",
            )
        )

    return issues


def check_h1(h1, h1_count):
    issues = []

    if not h1:
        issues.append(build_issue(ISSUE_MISSING_H1, MISSING_H1))
    elif h1_count > 1:
        issues.append(build_issue(ISSUE_MULTIPLE_H1, f"{MULTIPLE_H1} ({h1_count})"))

    return issues


def check_images(images_missing_alt):
    issues = []

    if images_missing_alt > 0:
        issues.append(
            build_issue(
                ISSUE_MISSING_IMAGE_ALT,
                f"{MISSING_IMAGE_ALT} ({images_missing_alt})",
            )
        )

    return issues


def run_seo_audit(seo_data):
    """
    seo_data = {
        title: str,
        meta_description: str,
        h1: str,
        h1_count: int,
        image_count: int,
        images_missing_alt: int
    }
    """
    issues = []

    issues.extend(check_title(seo_data.get("title")))
    issues.extend(check_meta_description(seo_data.get("meta_description")))
    issues.extend(check_h1(seo_data.get("h1"), seo_data.get("h1_count", 0)))
    issues.extend(check_images(seo_data.get("images_missing_alt", 0)))

    return issues


def run_seo_checks(seo_data):
    return [issue["message"] for issue in run_seo_audit(seo_data)]
