def project(row: dict, keys: list[str]) -> dict:
    """Select requested fields, requiring each to be present."""
    return {key: row[key] for key in keys}

def complete(row: dict, keys: list[str]) -> bool:
    """Indicate whether all requested fields are present.

    >>> complete({'x': 0}, ['x', 'y'])
    False
    """
    return all(key in row for key in keys)
