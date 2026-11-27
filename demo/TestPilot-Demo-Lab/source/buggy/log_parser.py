def message(line: str) -> str:
    """Extract everything after the first pipe."""
    return line.split('|')[1]

def error_lines(lines: list[str]) -> int:
    """Count lines whose level field is exactly ERROR."""
    return sum('ERROR' in line for line in lines)
