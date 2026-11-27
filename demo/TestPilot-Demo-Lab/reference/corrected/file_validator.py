def suffix_allowed(name: str, suffix: str) -> bool:
    """Match a case-insensitive suffix such as .csv on a supplied name."""
    return name.casefold().endswith(suffix.casefold())

def fits_budget(length: int, limit: int) -> bool:
    """Accept lengths up to and including the size budget."""
    return 0 <= length <= limit
