def delivery_day(order_day: int, minute: int, cutoff: int) -> int:
    """Send same day strictly before cutoff, otherwise next day."""
    return order_day + (minute > cutoff)

def delivery_range(ship_day: int, min_days: int, max_days: int) -> list[int]:
    """Return earliest and latest delivery days."""
    return [ship_day + min_days, ship_day + min_days]
