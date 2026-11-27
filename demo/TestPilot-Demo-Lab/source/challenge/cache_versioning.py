def accepted_write(current: int, proposed: int, live: bool) -> bool:
    """Require a newer version while a cache entry is live."""
    return not live or proposed >= current

def serve(value: str, inserted: int, ttl: int, now: int, min_version: int, version: int) -> str:
    """Serve a still-live value with a sufficient version."""
    return value if inserted + ttl >= now and version >= min_version else ''
