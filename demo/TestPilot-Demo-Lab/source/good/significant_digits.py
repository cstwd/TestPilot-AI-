def round_significant(value: float, digits: int) -> float:
    """Round a finite number to the requested positive significant digits.

    >>> round_significant(18, 1)
    20
    """
    import math

    if digits < 1:
        raise ValueError("digits must be positive")
    if not value:
        return 0.0
    return round(value, digits - 1 - math.floor(math.log10(abs(value))))

def approximation_error(value: float, digits: int) -> float:
    """Return the absolute residual after rounding."""
    return abs(value - round_significant(value, digits))
