def retry_delay(base: int, attempt: int, cap: int) -> int:
    """Use capped exponential waits for one-based retry attempts.

    >>> retry_delay(2, 2, 10)
    4
    """
    if attempt < 1:
        raise ValueError('attempt must be positive')
    return min(cap, base * 2 ** (attempt - 1))

def retry_budget(base: int, count: int, cap: int) -> int:
    """Sum the waits across the planned retries."""
    return sum(retry_delay(base, attempt, cap) for attempt in range(1, count + 1))
