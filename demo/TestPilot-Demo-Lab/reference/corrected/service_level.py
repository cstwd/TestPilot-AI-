def delay(actual: int, due: int) -> int:
    """Return positive delay or zero for early completion."""
    return max(0, actual - due)

def penalty(delay_minutes: int, grace: int, unit: int) -> int:
    """Charge per minute beyond the grace period."""
    return max(0, delay_minutes - grace) * unit
