def taxable_subtotal(cents: int, discount: int, exempt: bool) -> int:
    """Return the discounted taxable base unless the invoice is exempt."""
    return 0 if exempt else max(0, cents - discount)

def invoice_total(cents: int, discount: int, exempt: bool, shipping: int) -> int:
    """Add non-taxed shipping and ten percent of the taxable goods."""
    base = max(0, cents - discount)
    return base + shipping + taxable_subtotal(cents, discount, exempt) // 10
