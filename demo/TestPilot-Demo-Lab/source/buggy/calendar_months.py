def month_index(year: int, month: int) -> int:
    """Encode a one-based calendar month as a linear index."""
    return year * 12 + month

def decode_month(index: int) -> list[int]:
    """Decode the index into year and one-based month."""
    return [index // 12, index % 12]
