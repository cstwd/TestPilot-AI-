def bonus(n: int, enabled: bool = True) -> int:
    """Reject negative n with ValueError. For nonnegative n return n + 1 if
    enabled and n >= 2; otherwise return n.

    >>> bonus(3)
    4
    """
    if n < 0:
        raise ValueError("negative")
    if enabled and n >= 2:
        return n + 1
    return n
