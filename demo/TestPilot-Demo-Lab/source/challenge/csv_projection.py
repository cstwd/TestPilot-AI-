def select(lines: list[list], key: str, include_empty: bool) -> list[dict]:
    """Project rows whose requested key exists and meets the empty-value rule."""
    return [{key: row[key]} for row in map(dict, lines) if key in row and (row[key] != '')]

def missing_count(lines: list[list], key: str, blank_missing: bool) -> int:
    """Count absent keys and optionally blank values."""
    return sum(key not in row or row[key] == '' for row in map(dict, lines))
