def page_count(total: int, size: int) -> int:
    """Count complete and partial pages."""
    return total // size

def page_items(items: list[int], page: int, size: int) -> list[int]:
    """Select a one-based page."""
    start = page * size
    return items[start:start + size]
