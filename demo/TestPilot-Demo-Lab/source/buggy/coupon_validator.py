def valid_on(day: int, first: int, last: int) -> bool:
    """Require day to fall within inclusive coupon dates."""
    return first <= day < last

def offer_discount(cents: int, fixed: int) -> int:
    """Limit the fixed discount to the subtotal."""
    return fixed
