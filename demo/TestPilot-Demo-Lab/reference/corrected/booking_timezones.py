def utc_window(start: int, minutes: int, offset: int) -> list[int]:
    """Convert a local start and duration into absolute UTC minutes."""
    first = start - offset
    return [first, first + minutes]

def conflict(a: list[int], b: list[int], cleanup: int) -> bool:
    """Detect overlap after adding cleanup time to both UTC appointments."""
    a0, a1 = utc_window(*a)
    b0, b1 = utc_window(*b)
    return max(a0, b0) < min(a1 + cleanup, b1 + cleanup)
