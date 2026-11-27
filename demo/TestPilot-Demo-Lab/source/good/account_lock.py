def remaining_wait(now: int, locked_until: int) -> int:
    """Display remaining lock seconds for a synthetic account.

    >>> remaining_wait(20, 21)
    1
    """
    return max(0, locked_until - now)

def lock_notice(now: int, locked_until: int) -> str:
    """Render the lock countdown."""
    return f'{remaining_wait(now, locked_until)}s'
