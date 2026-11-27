def shipping_fee(cents: int, remote: bool) -> int:
    """Charge 500 below 5000 cents and add 200 to every remote shipment.

    >>> shipping_fee(1000, True)
    700
    """
    return (500 if cents < 5000 else 0) + (200 if remote else 0)

def grand_total(cents: int, remote: bool) -> int:
    """Add shipping to the subtotal."""
    return cents + shipping_fee(cents, remote)
