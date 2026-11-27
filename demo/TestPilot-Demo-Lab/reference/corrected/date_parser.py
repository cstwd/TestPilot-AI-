def iso_date(text: str) -> str:
    """Parse a valid date as YYYY-MM-DD."""
    from datetime import date

    return date.fromisoformat(text).isoformat()

def month_key(text: str) -> str:
    """Return the year and month of the parsed date."""
    return iso_date(text)[:7]
