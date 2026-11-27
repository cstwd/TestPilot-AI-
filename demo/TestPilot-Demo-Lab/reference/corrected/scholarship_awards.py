def award(score: int, income: int, renewal: bool) -> int:
    """Award a grant below the income ceiling with a renewal-adjusted score threshold."""
    return 500 if income < 30000 and score >= (75 if renewal else 85) else 0

def disbursement(total: int, installments: int, late: bool) -> list[int]:
    """Split an award with the remainder first, withholding the last part when late."""
    base, extra = divmod(total, installments)
    parts = [base + extra] + [base] * (installments - 1)
    return parts[:-1] if late else parts
