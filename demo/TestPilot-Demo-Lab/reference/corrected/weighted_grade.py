def grade(exam: int, project: int, excused: bool) -> int:
    """Weight exam at 60 percent, or use it alone if project is excused."""
    return exam if excused else (6 * exam + 4 * project) // 10

def passed(exam: int, project: int, excused: bool, incomplete: bool) -> bool:
    """Require a complete submission and a computed score of at least 60."""
    return not incomplete and grade(exam, project, excused) >= 60
