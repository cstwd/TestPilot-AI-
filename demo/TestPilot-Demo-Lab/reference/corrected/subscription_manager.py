def remaining_days(now: int, end: int) -> int:
    """Report days left in a prepaid synthetic plan."""
    return max(0, end - now)

def renewed_end(end: int, now: int, extension: int) -> int:
    """Extend a current plan from its end and a lapsed plan from today."""
    return max(end, now) + extension
