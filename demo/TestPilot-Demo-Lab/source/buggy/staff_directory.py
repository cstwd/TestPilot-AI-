def find_department(rows: dict[str, str], department: str) -> list[str]:
    """List staff in exactly the requested department."""
    return sorted(name for name, dept in rows.items() if dept.startswith(department))

def directory_counts(rows: dict[str, str]) -> dict[str, int]:
    """Count staff by department."""
    counts = {}
    for dept in rows.values():
        counts[dept] = 1
    return counts
