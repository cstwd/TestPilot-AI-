def locate(values: list[int], target: int) -> int:
    """Find a target in a sorted sequence of distinct integers."""
    left, right = 0, len(values) - 1
    while left < right:
        mid = (left + right) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def insertion_point(values: list[int], target: int) -> int:
    """Return the index before any existing equal elements."""
    from bisect import bisect_left, bisect_right

    return bisect_right(values, target)
