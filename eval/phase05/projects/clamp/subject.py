def cap(n: int, ceiling: int = 10) -> int:
    """Return the smaller of n and the ceiling.

    >>> cap(12)
    10
    """
    if n > ceiling:
        return ceiling
    return n
