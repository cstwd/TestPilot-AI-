def allocate(stock: int, reserved: int, request: int) -> int:
    """Fill at most free stock and at most requested units."""
    return min(request, max(0, stock - reserved))

def reorder(stock: int, reserved: int, incoming: int, threshold: int) -> bool:
    """Reorder when projected free stock is strictly below the threshold."""
    return max(0, stock - reserved) + incoming < threshold
