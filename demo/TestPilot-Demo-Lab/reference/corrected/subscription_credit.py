def credit(unused: int, monthly: int, term: int, prepaid: bool) -> int:
    """Prorate prepaid unused days, limiting credit to the monthly charge."""
    return min(monthly, monthly * max(0, unused) // term) if prepaid else 0

def rebill(unused: int, monthly: int, term: int, prepaid: bool, fee: int) -> int:
    """Deduct credit from a new fee and floor at zero."""
    return max(0, fee - credit(unused, monthly, term, prepaid))
