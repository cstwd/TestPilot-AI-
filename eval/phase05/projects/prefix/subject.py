def prefix_length(values: list) -> int:
    """Count entries before the first None.

    >>> prefix_length([4, None, 2])
    1
    """
    count = 0
    for value in values:
        if value is None:
            break
        count += 1
    return count
