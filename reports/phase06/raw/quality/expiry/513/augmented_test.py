import pytest
from subject import expired

def test_expired_at_limit_returns_false():
    """An item is not expired when age equals the limit."""
    assert expired(30, 30) is False

def test_expired_just_above_limit_returns_true():
    """An item is expired when age is one greater than the limit."""
    assert expired(31, 30) is True

def test_expired_with_default_limit():
    """Expired uses default limit of 30."""
    assert expired(31) is True
    assert expired(30) is False

def test_expired_zero_age():
    """Zero age is not expired for any non-negative limit."""
    assert expired(0, 2) is False

def test_expired_zero_limit():
    """Any positive age is expired when limit is zero."""
    assert expired(1, 0) is True
    assert expired(0, 0) is False

def test_expired_negative_age():
    """Negative age is not expired."""
    assert expired(-1, 30) is False

def test_expired_negative_limit():
    """Any age greater than a negative limit is expired."""
    assert expired(0, -1) is True

def test_expired_large_values():
    """Works with large values."""
    assert expired(1000000, 999999) is True
    assert expired(999999, 1000000) is False

def test_expired_returns_bool_type():
    """Function returns a boolean type."""
    result = expired(31, 30)
    assert isinstance(result, bool)
    result = expired(30, 30)
    assert isinstance(result, bool)

def test_expired_keyword_arguments():
    """Function works with keyword arguments."""
    assert expired(age=31, limit=30) is True
    assert expired(age=30, limit=30) is False

def test_expired_mixed_positional_keyword():
    """Function works with mixed positional and keyword arguments."""
    assert expired(31, limit=30) is True
    assert expired(age=30, limit=30) is False
