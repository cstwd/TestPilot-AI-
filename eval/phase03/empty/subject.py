def first_or_default(values: list[int], default: int = 0) -> int:
    """Return the first element, or the chosen default for an empty list.

    >>> first_or_default([0, 9])
    0
    >>> first_or_default([], 7)
    7
    """
    return values[0]
