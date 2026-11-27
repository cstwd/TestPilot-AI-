def assignment(available: bool, qualified: bool, hours: int) -> str:
    """Assign only an available qualified worker below the weekly limit."""
    return 'assigned' if available and qualified and hours < 40 else 'waiting'

def shift_credit(hours: int, holiday: bool, training: bool) -> int:
    """Double holiday hours for regular work only."""
    return hours * (2 if holiday and not training else 1)
