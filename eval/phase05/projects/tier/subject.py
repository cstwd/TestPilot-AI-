def tier(points: int) -> str:
    """Gold starts at 100, silver at 50, otherwise basic.

    >>> tier(120)
    'gold'
    """
    if points >= 100:
        return "gold"
    if points >= 50:
        return "silver"
    return "basic"
