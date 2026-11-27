def pop_next(values: list[str]) -> list[str]:
    """Return the remaining FIFO queue after one removal."""
    return values[:-1]

def queue_item(values: list[str], position: int) -> str:
    """Read the item at a one-based queue position."""
    if position < 1:
        raise ValueError('position must be positive')
    return values[position]
