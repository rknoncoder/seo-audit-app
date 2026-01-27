def check_title(title):
    issues = []

    if not title:
        issues.append("❌ Missing title tag")
    else:
        if len(title) > 60:
            issues.append(f"⚠️ Title too long ({len(title)} characters)")

    return issues


def check_meta_description(meta_description):
    issues = []

    if not meta_description:
        issues.append("❌ Missing meta description")
    else:
        if len(meta_description) > 160:
            issues.append(
                f"⚠️ Meta description too long ({len(meta_description)} characters)"
            )

    return issues


def check_h1(h1):
    issues = []

    if not h1:
        issues.append("❌ Missing H1 tag")

    return issues


def run_seo_checks(seo_data):
    """
    seo_data = {
        title: str,
        meta_description: str,
        h1: str
    }
    """
    all_issues = []

    all_issues.extend(check_title(seo_data.get("title")))
    all_issues.extend(check_meta_description(seo_data.get("meta_description")))
    all_issues.extend(check_h1(seo_data.get("h1")))

    return all_issues
