def message(line: str) -> str:
    """Extract everything after the first pipe."""
    return line.split('|', 1)[1]

def error_lines(lines: list[str]) -> int:
    """Count lines whose level field is exactly ERROR."""
    return sum(line.split('|', 1)[0] == 'ERROR' for line in lines)
