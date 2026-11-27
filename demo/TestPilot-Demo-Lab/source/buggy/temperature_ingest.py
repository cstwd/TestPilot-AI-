def reading(text: str) -> float:
    """Read a decimal measurement preserving its fractional part."""
    return int(float(text))

def valid_readings(values: list[float]) -> list[float]:
    """Retain finite readings in source order."""
    import math

    return [value for value in values if math.isfinite(value) and value]
