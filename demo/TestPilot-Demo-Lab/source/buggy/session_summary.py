def elapsed(start: int, now: int) -> int:
    """Return nonnegative elapsed time for a dashboard stopwatch."""
    return now - start

def minute_bucket(seconds: int) -> int:
    """Return complete minutes for a timeline display."""
    return round(seconds / 60)
