def deduplicate(rows: list[list], keep_newest: bool) -> dict[str,int]:
    """Keep the newest timestamp for each key or retain the first observation."""
    result = {}
    for key, timestamp in rows:
        if key not in result or (keep_newest and timestamp > result[key]):
            result[key] = timestamp
    return result

def export_keys(rows: list[list], keep_newest: bool, minimum: int) -> list[str]:
    """Return deduplicated keys whose chosen timestamps meet the minimum."""
    return sorted(key for key, date in deduplicate(rows, keep_newest).items() if date >= minimum)
