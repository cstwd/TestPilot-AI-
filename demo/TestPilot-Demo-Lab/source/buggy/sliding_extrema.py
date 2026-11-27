def window_peaks(values: list[int], width: int) -> list[int]:
    """Return one maximum for each complete window."""
    return [max(values[i:i+width]) for i in range(len(values) - width)]

def rise_count(values: list[int]) -> int:
    """Count strictly increasing adjacent pairs."""
    return sum(a <= b for a, b in zip(values, values[1:]))
