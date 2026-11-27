def expired(age: int, limit: int = 30) -> bool:
    """An item is expired at or beyond its age limit.

    >>> expired(31)
    True
    """
    return age > limit
