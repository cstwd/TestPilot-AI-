def service_due(hours: int, days: int, heavy: bool) -> bool:
    """Trigger service at the adjusted hours limit or after 90 days."""
    return hours >= (200 if heavy else 120) or days >= 90

def service_slot(due: bool, parts: bool, minutes: int) -> str:
    """Reserve a slot only when due, stocked, and long enough."""
    return 'reserve' if due and parts and minutes > 45 else 'defer'
