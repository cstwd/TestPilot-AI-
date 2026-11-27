def valid_slot(start: int, end: int, latest: int) -> bool:
    """Accept a positive-width interval within the booking day.

    >>> valid_slot(0, 6, 6)
    True
    """
    return 0 <= start < end <= latest

def booking_length(start: int, end: int, latest: int) -> int:
    """Return duration for a valid booking."""
    if not valid_slot(start, end, latest):
        raise ValueError('outside booking hours')
    return end - start
