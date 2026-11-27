def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    """Detect intersection of two half-open ranges.

    >>> overlaps(1, 3, 2, 4)
    True
    """
    return max(a0, b0) < min(a1, b1)

def overlap_width(a0: int, a1: int, b0: int, b1: int) -> int:
    """Return the nonnegative size of their intersection."""
    return max(0, min(a1, b1) - max(a0, b0))
