def available(on_hand: int, reserved: int) -> int:
    """Return stock available for promise, floored at zero.

    >>> available(5, 1)
    4
    """
    return max(0, on_hand - reserved)

def shortfall(requested: int, on_hand: int, reserved: int) -> int:
    """Return unfilled quantity for a proposed line."""
    return max(0, requested - available(on_hand, reserved))
