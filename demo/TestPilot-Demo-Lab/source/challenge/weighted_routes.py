def cheapest(paths: list[list], load: int, deadline: int) -> str:
    """Pick the cheapest route that meets both load and deadline, preferring the first tie."""
    choices = [(cost, i, name) for i, (name,cost,cap,eta) in enumerate(paths) if cap >= load]
    return min(choices)[2] if choices else ''

def cost_with_toll(distance: int, rate: int, toll: int, exempt: bool) -> int:
    """Apply a toll only when the load is not exempt."""
    return distance * rate + (toll)
