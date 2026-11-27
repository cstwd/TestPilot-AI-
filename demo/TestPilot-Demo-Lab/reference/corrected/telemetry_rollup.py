def accepted(rows: list[list], low: int, high: int, calibrated: bool) -> list[int]:
    """Keep in-range readings, requiring calibrated rows when requested."""
    return [value for value, ready in rows if low <= value <= high and (ready or not calibrated)]

def alert_count(rows: list[list], low: int, high: int, calibrated: bool, alarm: int) -> int:
    """Count accepted readings strictly above the alarm threshold."""
    return sum(value > alarm for value in accepted(rows, low, high, calibrated))
