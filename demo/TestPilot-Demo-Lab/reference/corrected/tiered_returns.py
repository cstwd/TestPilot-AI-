def refund(cents: int, units: int, opened: bool, member: bool) -> int:
    """Deduct a flat fee only for opened goods returned by nonmembers."""
    gross = cents * units
    return max(0, gross - (250 if opened and not member else 0))

def return_window(delivered: int, requested: int, member: bool) -> bool:
    """Allow requests from delivery through the member-adjusted final day."""
    return 0 <= requested - delivered <= (45 if member else 30)
