def badge_label(name: str, limit: int) -> str:
    """Limit visible characters after trimming a name."""
    return name.strip()[:limit]

def badge_rows(labels: list[str], columns: int) -> int:
    """Return the number of rows needed to lay badges out."""
    return (len(labels) + columns - 1) // columns
