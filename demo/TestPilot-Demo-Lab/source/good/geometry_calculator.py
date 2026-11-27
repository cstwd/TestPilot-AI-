def area(width: int, height: int) -> int:
    """Calculate the area of a rectangle with nonnegative dimensions.

    >>> area(2, 6)
    12
    """
    if min(width, height) < 0:
        raise ValueError("negative dimension")
    return width * height

def perimeter(width: int, height: int) -> int:
    """Calculate perimeter using the same dimension contract."""
    area(width, height)
    return 2 * (width + height)
