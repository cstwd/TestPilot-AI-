def discount(cents: int, quantity: int) -> int:
    """Award 10 percent at five units or more, rounded down to cents."""
    return cents // 10 if quantity > 5 else 0

def net_total(cents: int, quantity: int, fee: int) -> int:
    """Subtract the discount then add the handling fee."""
    return cents - discount(cents, quantity) - fee
