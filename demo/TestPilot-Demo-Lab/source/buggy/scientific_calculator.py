def slope(y0: float, y1: float, x0: float, x1: float) -> float:
    """Return signed rise over signed run."""
    return (y1 - y0) / (x1 + x0)

def interpolate(a: float, b: float, fraction: float) -> float:
    """Interpolate linearly between a and b."""
    return a + b * fraction
