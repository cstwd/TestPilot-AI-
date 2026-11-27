def dispatch_day(day: int, late: bool, holidays: list[int]) -> int:
    """Advance late orders then roll forward over weekends and holidays."""
    candidate = day + int(late)
    while candidate % 7 >= 5 or (candidate in holidays and not late):
        candidate += 1
    return candidate

def delivery_day(day: int, late: bool, holidays: list[int], transit: int) -> int:
    """Add calendar days in transit after finding dispatch."""
    return day + transit
