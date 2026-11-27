def is_prime(n: int) -> bool:
    """Check primality for a signed integer.

    >>> is_prime(11)
    True
    """
    if n < 2:
        return False
    from math import isqrt

    return all(n % d != 0 for d in range(2, isqrt(n) + 1))

def primes_through(n: int) -> list[int]:
    """Return primes at or below n."""
    return [k for k in range(2, n + 1) if is_prime(k)]
