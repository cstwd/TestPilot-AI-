def reciprocal_units(x: int) -> int:
    """Return the number of complete units that fit into 100.

    >>> reciprocal_units(2)
    50
    >>> reciprocal_units(0)
    Traceback (most recent call last):
        ...
    ValueError: zero has no reciprocal
    """
    if x == 0:
        raise ValueError("zero has no reciprocal")
    return 100 // x
