def assign_track(talk: str, remote: bool, seats: int) -> str:
    """Assign live talks only when room seats are available."""
    if remote or seats <= 0:
        return 'online'
    return talk

def room_count(onsite: int, remote: int, room_size: int, hybrid: bool) -> int:
    """Round up room needs, including remote speakers only in hybrid recording rooms."""
    demand = onsite + (remote if hybrid else 0)
    return (demand + room_size - 1) // room_size
