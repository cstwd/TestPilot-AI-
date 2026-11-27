def ranked(rows: list[list]) -> list[list]:
    """Sort by score ascending, preserving tie order."""
    return sorted(rows, key=lambda row: (row[1], row[0]))

def lowest(values: list[int], count: int) -> list[int]:
    """Return the count smallest values in ascending order."""
    return sorted(values)[-count:]
