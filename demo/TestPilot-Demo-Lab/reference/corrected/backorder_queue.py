def take_orders(queue: list[str], count: int) -> list[str]:
    """Return the first count waiting orders."""
    return queue[:count]

def waiting_after(queue: list[str], filled: list[str]) -> list[str]:
    """Return still-open orders retaining queue order."""
    return [order for order in queue if order not in filled]
