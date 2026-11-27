def quicksort(values: list[int]) -> list[int]:
    """Return a new ascending list, preserving repeated elements.

    >>> quicksort([3, -2, 3, 0])
    [-2, 0, 3, 3]
    >>> quicksort([])
    []
    >>> quicksort([7])
    [7]
    """
    if len(values) < 2:
        return list(values)
    pivot = values[len(values) // 2]
    lower, equal, higher = [], [], []
    for value in values:
        if value < pivot:
            lower.append(value)
        elif value > pivot:
            higher.append(value)
        else:
            equal.append(value)
    return quicksort(lower) + equal + quicksort(higher)
