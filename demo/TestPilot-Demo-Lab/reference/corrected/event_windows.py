def window_start(time: int, width: int) -> int:
    """Align a tick to the start of its fixed-width window."""
    return time // width * width

def events_in_window(times: list[int], start: int, width: int) -> int:
    """Count ticks in a half-open time window."""
    return sum(start <= tick < start + width for tick in times)
