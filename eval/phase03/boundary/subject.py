def valid_index(index: int, length: int) -> bool:
    """Check whether index lies inside a zero-based sequence of the given length.

    >>> valid_index(0, 3)
    True
    >>> valid_index(2, 3)
    True
    >>> valid_index(3, 3)
    False
    >>> valid_index(-1, 3)
    False
    """
    return 0 <= index <= length
