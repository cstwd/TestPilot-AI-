def parse_count(text: str) -> int:
    """Parse an integer count; raise ValueError on malformed text.

    >>> parse_count("12")
    12
    >>> parse_count("unknown")
    Traceback (most recent call last):
        ...
    ValueError: invalid count
    """
    try:
        return int(text)
    except ValueError:
        return 0
