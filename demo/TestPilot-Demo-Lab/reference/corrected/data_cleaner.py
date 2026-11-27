def clean_tags(tags: list[str]) -> list[str]:
    """Trim tags and drop whitespace-only entries."""
    return [tag.strip() for tag in tags if tag.strip()]

def coalesce(values: list[int | None], fill: int) -> list[int]:
    """Replace nulls while preserving valid zeros."""
    return [fill if value is None else value for value in values]
