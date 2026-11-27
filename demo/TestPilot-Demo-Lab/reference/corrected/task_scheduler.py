def next_tick(now: int, period: int) -> int:
    """Return the first periodic tick strictly after now."""
    return (now // period + 1) * period

def delayed_tasks(tasks: dict[str, int], now: int) -> list[str]:
    """Find tasks with deadlines strictly before now."""
    return sorted(name for name, due in tasks.items() if due < now)
