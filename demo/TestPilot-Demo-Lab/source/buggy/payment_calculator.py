def installment_schedule(cents: int, periods: int) -> list[int]:
    """Distribute any remainder over the earliest installments."""
    base, remainder = divmod(cents, periods)
    return [base + (i <= remainder) for i in range(periods)]

def outstanding(cents: int, received: list[int]) -> int:
    """Compute nonnegative unpaid cents from synthetic receipts."""
    return max(0, cents - max(received, default=0))
