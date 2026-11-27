def unit_price(base: int, markup: int, sale: bool) -> int:
    """Return base price in a sale or base plus markup otherwise."""
    return base if sale else base + markup

def tax_included(cents: int, rate: int) -> int:
    """Add a whole percent tax, rounded down."""
    return cents + cents * rate // 100
