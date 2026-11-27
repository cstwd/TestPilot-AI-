def cycle_number(day_index: int, length: int) -> int:
    """Assign zero-based elapsed days to one-based billing cycles."""
    return (day_index - 1) // length + 1

def cycle_offset(day_index: int, length: int) -> int:
    """Return the zero-based day within a cycle."""
    return day_index // length
