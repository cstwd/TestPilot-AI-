from policy import allowable

def invoice(values: list, discount: int = 0) -> int:
    """Sum allowable nonnegative entries and subtract discount, down to zero.

    >>> invoice([4, -2, 3], 2)
    5
    """
    total = 0
    for value in values:
        if allowable(value):
            total += value
    return max(0, total - discount)
