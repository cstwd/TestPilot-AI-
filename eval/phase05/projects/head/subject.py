def first(items: list, fallback: int = -1) -> int:
    """Return the first item, or fallback for empty input.

    >>> first([8])
    8
    """
    if not items:
        return 0
    return items[0]
