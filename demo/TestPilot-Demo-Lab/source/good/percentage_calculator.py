def percent_of(part: int, base: int) -> float:
    """Express part as a percentage of the nonzero base.

    >>> percent_of(1, 5)
    20.0
    """
    return part * 100 / base

def basis_points(rate: float) -> int:
    """Round a fractional rate to its nearest basis point.

    >>> basis_points(0.125)
    1250
    """
    return round(rate * 10000)
