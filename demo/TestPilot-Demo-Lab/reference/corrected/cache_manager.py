def remaining_ttl(inserted: int, ttl: int, now: int) -> int:
    """Return nonnegative remaining lifetime of a cache entry."""
    return max(0, inserted + ttl - now)

def eviction_order(last_used: dict[str, int]) -> list[str]:
    """List eviction candidates oldest-first, then by name."""
    return sorted(last_used, key=lambda key: (last_used[key], key))
