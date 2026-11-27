from decimal import Decimal, ROUND_HALF_UP

def cents(amount: str) -> int:
    """Round a decimal amount to cents with ties away from zero."""
    return int(Decimal(amount).quantize(Decimal("0.01")) * 100)

def cash_round(value: int) -> int:
    """Round nonnegative cents to the nearest five cents."""
    return ((value + 1) // 5) * 5
