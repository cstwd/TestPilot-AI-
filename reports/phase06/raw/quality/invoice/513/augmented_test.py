import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('def allowable(value):\n    return value >= 0\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import invoice

def test_docstring_example():
    """Verify the documented doctest example."""
    assert invoice([4, -2, 3], 2) == 5

def test_empty_list_returns_zero():
    """An empty list with any discount should return 0."""
    assert invoice([], 2) == 0

def test_all_negative_values_returns_zero():
    """If all values are negative, the total is 0, so result is 0."""
    assert invoice([-1, -5, -10], 0) == 0

def test_discount_exceeds_total_returns_zero():
    """If discount is greater than the sum of allowable values, result is 0."""
    assert invoice([1], 2) == 0

def test_no_discount_returns_sum():
    """With no discount, the result is the sum of allowable values."""
    assert invoice([1, 2, 3], 0) == 6

def test_mixed_values_with_discount():
    """Only non-negative values are summed, then discount is applied."""
    assert invoice([10, -5, 5, -1], 3) == 12

def test_zero_value_is_allowable():
    """Zero is non-negative and should be included in the sum."""
    assert invoice([0, 0, 0], 0) == 0

def test_single_value_no_discount():
    """A single positive value with no discount returns that value."""
    assert invoice([7], 0) == 7

def test_discount_equals_total():
    """If discount equals the total, the result should be 0."""
    assert invoice([5, 5], 10) == 0

def test_large_values():
    """Test with larger values to ensure no overflow or logic issues."""
    assert invoice([1000, 2000, -500], 500) == 2500
