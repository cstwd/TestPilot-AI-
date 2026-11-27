def subtotal_after_discount(cents: int, gold: bool, coupon: int) -> int:
    """Apply the qualifying Gold discount before a fixed coupon and floor at zero."""
    loyalty = cents // 10 if gold and cents >= 2000 else 0
    return max(0, cents - loyalty - coupon)

def checkout(cents: int, gold: bool, coupon: int, pickup: bool) -> int:
    """Add shipping when delivery is requested and the discounted subtotal is below 3000."""
    subtotal = subtotal_after_discount(cents, gold, coupon)
    return subtotal + (400 if not pickup and subtotal < 3000 else 0)
