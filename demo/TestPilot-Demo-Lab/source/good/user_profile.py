def display_name(given: str, family: str) -> str:
    """Join and trim supplied names."""
    return ' '.join(part.strip() for part in (given, family) if part.strip())

def initials(given: str, family: str) -> str:
    """Return uppercase initials."""
    return ''.join(part[0].upper() for part in display_name(given, family).split())
