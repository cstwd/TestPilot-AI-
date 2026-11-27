def cart_total(lines: list[list[int]]) -> int:
    """Total integer-cent prices multiplied by quantities.

    >>> cart_total([[300, 3]])
    900
    """
    return sum(price * count for price, count in lines)

def item_count(lines: list[list[int]]) -> int:
    """Sum quantities across the cart."""
    return sum(count for _, count in lines)
