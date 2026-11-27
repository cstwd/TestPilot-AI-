def normalize_username(value: str) -> str:
    """Trim and case-fold a nonempty display handle."""
    normalized = value.strip().casefold()
    if not normalized:
        raise ValueError('empty handle')
    return normalized

def handles_match(left: str, right: str) -> bool:
    """Compare canonical display handles."""
    return normalize_username(left) == normalize_username(right)
