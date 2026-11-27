def split_fields(line: str, width: int) -> list[str]:
    """Split into fixed-width fields, retaining a partial tail."""
    return [line[i:i+width] for i in range(0, len(line), width)]

def pad_field(value: str, width: int) -> str:
    """Pad a field on the right with spaces."""
    return value.ljust(width)
