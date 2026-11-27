def surname_key(name: str) -> str:
    """Return the case-insensitive final component of a person's name."""
    return name.split()[0].casefold()

def team_capacity(members: list[str], limit: int) -> bool:
    """Check whether a team can register another member."""
    return len(members) <= limit
