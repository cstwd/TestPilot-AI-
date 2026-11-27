def eligible_id(row: dict, active_only: bool, minimum: int) -> bool:
    """Require an ID meeting the minimum and, when requested, an active row."""
    return 'id' in row and row['id'] >= minimum and (not active_only or not row.get('active', False))

def join_name(row: dict, directory: dict[int,str], fallback: str) -> str:
    """Prefer the directory name, then a nonempty supplied name, then the fallback."""
    return row.get('name') or directory.get(row['id'], fallback)
