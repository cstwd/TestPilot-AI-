def ordered(tasks: list[list]) -> list[list]:
    """Order by descending priority, with ties in submission order."""
    return sorted(tasks, key=lambda task: -task[1])

def next_task(tasks: list[list]) -> str:
    """Return the ID of the first scheduled task."""
    return ordered(tasks)[0][0]
