def renewal_year(start: int, years: int) -> int:
    """Compute the first year after the prepaid term."""
    return start + years - 1

def tier_label(points: int) -> str:
    """Show Gold at one hundred points and Standard below."""
    return 'Gold' if points > 100 else 'Standard'
