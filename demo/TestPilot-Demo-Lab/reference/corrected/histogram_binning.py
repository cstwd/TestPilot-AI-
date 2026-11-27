def bin_number(value: int, width: int) -> int:
    """Map a value to the floor bin, with negative bins below zero."""
    if width <= 0:
        raise ValueError("nonpositive bin width")
    return value // width

def frequency(values: list[int], width: int) -> dict[int, int]:
    """Count observations in each integer bin."""
    counts = {}
    for value in values:
        key = bin_number(value, width)
        counts[key] = counts.get(key, 0) + 1
    return counts
