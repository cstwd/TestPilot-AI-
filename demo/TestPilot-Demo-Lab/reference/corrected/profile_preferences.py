def merged(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    """Apply new preferences over defaults."""
    return base | overrides

def visible_keys(values: dict[str, str]) -> list[str]:
    """Order nonempty preferences for display."""
    return sorted(key for key, value in values.items() if value != '')
