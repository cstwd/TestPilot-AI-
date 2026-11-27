def leap(year: int) -> bool:
    """Use Gregorian leap-year rules.

    >>> leap(2024)
    True
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_year(year: int) -> int:
    """Return the length of a Gregorian year."""
    return 366 if leap(year) else 365
