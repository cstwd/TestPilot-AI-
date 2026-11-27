def push(stack: list[int], value: int) -> list[int]:
    """Return a stack with value on top, leaving the input alone.

    >>> push([1], 3)
    [1, 3]
    """
    return stack + [value]

def top(stack: list[int]) -> int:
    """Read the top item of a nonempty stack."""
    return stack[-1]
