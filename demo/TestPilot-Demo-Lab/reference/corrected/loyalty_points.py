def earn(cents: int, multiplier: int) -> int:
    """Award points for complete cents-per-dollar units before multiplying."""
    return (cents // 100) * multiplier

def spend(balance: int, points: int) -> int:
    """Redeem at most the available balance."""
    if points > balance:
        raise ValueError('insufficient points')
    return balance - points
