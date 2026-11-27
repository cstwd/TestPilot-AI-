def eligible(rows: list[list], min_score: int, archived: bool) -> list[str]:
    """Select scored records and include archived ones only when requested."""
    return [name for name, score, old in rows if score >= min_score and (archived or not old)]

def result_page(rows: list[list], min_score: int, archived: bool, page: int, size: int) -> list[str]:
    """Apply eligibility before slicing a one-based page."""
    items = eligible(rows, min_score, archived)
    start = (page - 1) * size
    return items[start:start + size]
