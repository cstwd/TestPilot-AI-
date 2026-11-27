import pytest
from subject import bonus

def test_bonus_negative_raises_value_error():
    """Reject negative n with ValueError."""
    with pytest.raises(ValueError):
        bonus(-1)

def test_bonus_zero_enabled_returns_zero():
    """For n=0, enabled=True, n < 2, so return n."""
    assert bonus(0, enabled=True) == 0

def test_bonus_one_enabled_returns_one():
    """For n=1, enabled=True, n < 2, so return n."""
    assert bonus(1, enabled=True) == 1

def test_bonus_two_enabled_returns_three():
    """For n=2, enabled=True, n >= 2, so return n + 1."""
    assert bonus(2, enabled=True) == 3

def test_bonus_three_enabled_returns_four():
    """For n=3, enabled=True, n >= 2, so return n + 1."""
    assert bonus(3, enabled=True) == 4

def test_bonus_two_disabled_returns_two():
    """For n=2, enabled=False, return n."""
    assert bonus(2, enabled=False) == 2

def test_bonus_three_disabled_returns_three():
    """For n=3, enabled=False, return n."""
    assert bonus(3, enabled=False) == 3

def test_bonus_zero_disabled_returns_zero():
    """For n=0, enabled=False, return n."""
    assert bonus(0, enabled=False) == 0

def test_bonus_negative_one_raises_value_error():
    """Reject n=-1 with ValueError."""
    with pytest.raises(ValueError):
        bonus(-1, enabled=True)

def test_bonus_negative_large_raises_value_error():
    """Reject n=-100 with ValueError."""
    with pytest.raises(ValueError):
        bonus(-100, enabled=False)

def test_bonus_default_enabled_is_true():
    """Default enabled is True, so bonus(3) should return 4."""
    assert bonus(3) == 4

def test_bonus_default_enabled_zero():
    """Default enabled is True, so bonus(0) should return 0."""
    assert bonus(0) == 0

def test_bonus_default_enabled_one():
    """Default enabled is True, so bonus(1) should return 1."""
    assert bonus(1) == 1

def test_bonus_default_enabled_two():
    """Default enabled is True, so bonus(2) should return 3."""
    assert bonus(2) == 3
