def earn(cents: int, multiplier: int) -> int:
    """Award points for complete cents-per-dollar units before multiplying."""
    return cents * multiplier // 100

def spend(balance: int, points: int) -> int:
    """Redeem at most the available balance."""
    if points >= balance:
        raise ValueError('insufficient points')
    return balance - points
