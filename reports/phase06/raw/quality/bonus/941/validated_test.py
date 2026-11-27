import pytest
from subject import bonus

def test_negative_n_raises_value_error():
    """Reject negative n with ValueError."""
    with pytest.raises(ValueError):
        bonus(-1)

def test_zero_returns_zero_when_enabled():
    """For n=0 and enabled=True, return n (0)."""
    assert bonus(0, enabled=True) == 0

def test_one_returns_one_when_enabled():
    """For n=1 and enabled=True, return n (1)."""
    assert bonus(1, enabled=True) == 1

def test_two_returns_three_when_enabled():
    """For n=2 and enabled=True, return n + 1 (3)."""
    assert bonus(2, enabled=True) == 3

def test_three_returns_four_when_enabled():
    """For n=3 and enabled=True, return n + 1 (4)."""
    assert bonus(3, enabled=True) == 4

def test_two_returns_two_when_disabled():
    """For n=2 and enabled=False, return n (2)."""
    assert bonus(2, enabled=False) == 2

def test_three_returns_three_when_disabled():
    """For n=3 and enabled=False, return n (3)."""
    assert bonus(3, enabled=False) == 3

def test_negative_n_raises_even_when_disabled():
    """Negative n raises ValueError regardless of enabled flag."""
    with pytest.raises(ValueError):
        bonus(-5, enabled=False)
