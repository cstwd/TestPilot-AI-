def local_minute(utc_minute: int, offset: int) -> int:
    """Apply a fixed offset and wrap within a day.

    >>> local_minute(1435, 30)
    25
    """
    return (utc_minute + offset) % 1440

def day_shift(utc_minute: int, offset: int) -> int:
    """Return the offset-induced signed day shift."""
    return (utc_minute + offset) // 1440
