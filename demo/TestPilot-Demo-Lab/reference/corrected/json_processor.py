def parse_record(text: str) -> dict:
    """Load a JSON object from a supplied string."""
    import json

    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError('expected object')
    return result

def field_or(row: dict, key: str, default: int) -> int:
    """Use the default only for an absent key."""
    return row.get(key, default)
