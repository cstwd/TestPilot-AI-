def word_count(text: str) -> int:
    """Count whitespace-delimited tokens.

    >>> word_count('alpha  beta')
    2
    """
    return len(text.split())

def longest_token(text: str) -> str:
    """Return the first longest token, or empty text."""
    return max(text.split(), key=len, default='')
