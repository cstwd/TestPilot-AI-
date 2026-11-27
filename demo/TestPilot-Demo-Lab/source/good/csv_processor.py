def rows(text: str) -> list[list[str]]:
    """Read CSV from literal text, including quoted fields."""
    import csv
    import io

    return list(csv.reader(io.StringIO(text, newline='')))

def header_width(text: str) -> int:
    """Return first-record width, or zero for empty text."""
    parsed = rows(text)
    return len(parsed[0]) if parsed else 0
