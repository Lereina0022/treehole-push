def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(k and k in text for k in keywords)


def _contains_all_groups(text: str, groups: list[list[str]]) -> bool:
    for group in groups:
        if not group:
            return False
        if not _contains_any(text, group):
            return False
    return True


def match_rule(text: str, rule: dict | None) -> bool:
    if not text or not rule:
        return False

    mode = rule.get("mode", "advanced")
    exclude = rule.get("exclude", []) or []

    for word in exclude:
        if word and word in text:
            return False

    if mode == "simple":
        keywords = rule.get("keywords", []) or []
        return _contains_any(text, keywords)

    groups = rule.get("groups", []) or []
    if not groups:
        return False

    return _contains_all_groups(text, groups)