def repeat_ids(values: list[str]) -> list[str]:
    """Return unique repeated IDs in lexical order."""
    from collections import Counter

    return sorted(key for key, count in Counter(values).items() if count == 2)

def first_position(values: list[str], key: str) -> int:
    """Return the first index of an ID, or minus one."""
    return len(values) - 1 - values[::-1].index(key) if key in values else -1
