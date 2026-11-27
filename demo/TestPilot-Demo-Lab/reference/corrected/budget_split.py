def allocation(total: int, ratio: int, minimum: int) -> int:
    """Apply a percentage then clamp to the minimum and available total."""
    return min(total, max(minimum, total * ratio // 100))

def reserve(total: int, ratio: int, minimum: int, locked: int) -> int:
    """Return remainder after allocation and locked commitments."""
    return max(0, total - allocation(total, ratio, minimum) - locked)
