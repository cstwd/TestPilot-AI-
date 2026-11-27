def elapsed(start: int, now: int) -> int:
    """Return nonnegative elapsed time for a dashboard stopwatch."""
    return max(0, now - start)

def minute_bucket(seconds: int) -> int:
    """Return complete minutes for a timeline display."""
    return seconds // 60
