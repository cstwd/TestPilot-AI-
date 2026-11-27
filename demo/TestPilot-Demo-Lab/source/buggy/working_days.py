def is_workday(day: int) -> bool:
    """Interpret Monday as day zero and repeat weekly."""
    return day % 7 <= 5

def business_days(start: int, end: int) -> int:
    """Count weekdays in a half-open day range."""
    return sum(is_workday(day) for day in range(start, end + 1))
