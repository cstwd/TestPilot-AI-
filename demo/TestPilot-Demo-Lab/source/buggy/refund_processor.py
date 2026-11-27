def refund_amount(unit: int, returned: int, restocking: int) -> int:
    """Deduct one restocking fee from the returned line and floor at zero."""
    return max(0, unit * returned - restocking * returned)

def return_units(ordered: int, prior_returns: int) -> int:
    """Return maximum remaining returnable units."""
    return ordered - prior_returns
