from tariff import BASE

def freight(units: int) -> int:
    """Return base freight plus the unit count.

    >>> freight(3)
    8
    """
    return BASE + units
