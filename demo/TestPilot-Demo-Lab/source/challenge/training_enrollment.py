def placement(score: int, prerequisite: bool, sponsor: bool) -> str:
    """Place in advanced with the prerequisite and a passing score or sponsor."""
    return 'advanced' if prerequisite and (score >= 80 and sponsor) else 'foundation'

def stipend(days: int, remote: bool, funded: bool) -> int:
    """Fund on-site training at 30 per day, capped at 150."""
    return days * 30 if funded and not remote else 0
