def settlement(gross: int, fee_bp: int) -> int:
    """Deduct the fee in basis points, rounding down the fee."""
    return gross - gross * fee_bp // 10000

def unsettled(rows: list[list]) -> int:
    """Sum the amount of pending settlement rows."""
    return sum(amount for amount, state in rows if state == 'pending')
