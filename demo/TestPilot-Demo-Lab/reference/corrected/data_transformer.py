def columns(values: list[list[int]]) -> list[list[int]]:
    """Transpose equal length rows, rejecting ragged rows."""
    return [list(column) for column in zip(*values, strict=True)]

def rename_field(row: dict, old: str, new: str) -> dict:
    """Return a copy with the given field moved to its new key."""
    result = row.copy()
    result[new] = result.pop(old)
    return result
