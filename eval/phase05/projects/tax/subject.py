from policy import RATE

def tax(cents: int) -> int:
    """Compute a percentage in whole cents, rounded upwards.

    >>> tax(100)
    5
    """
    return cents * RATE // 100
