def calibrated(raw: int, zero: int, gain: int, limit: int) -> int:
    """Adjust offset before gain, then clamp to the signed limit."""
    value = (raw - zero) * gain
    return max(-limit, min(limit, value))

def within_band(value: int, center: int, tolerance: int, inclusive: bool) -> bool:
    """Compare the absolute residual with the selected boundary policy."""
    delta = abs(value - center)
    return delta <= tolerance if inclusive else delta < tolerance
