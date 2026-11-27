import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('RATE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from policy import RATE
from subject import tax

def test_tax_example_1():
    """Test the doctest example: tax(100) should return 5."""
    assert tax(100) == 5

def test_tax_zero():
    """Test boundary value: tax(0) should return 0."""
    assert tax(0) == 0

def test_tax_one():
    """Test with 1 cent: should return 0 (5% of 1 is 0.05, rounded down to 0)."""
    assert tax(1) == 0

def test_tax_100():
    """Test with 100 cents: 5% of 100 is 5."""
    assert tax(100) == 5

def test_tax_101():
    """Test with 101 cents: 5% of 101 is 5.05, integer division gives 5."""
    assert tax(101) == 5

def test_tax_199():
    """Test with 199 cents: 5% of 199 is 9.95, integer division gives 9."""
    assert tax(199) == 9

def test_tax_200():
    """Test with 200 cents: 5% of 200 is 10."""
    assert tax(200) == 10

def test_tax_1000():
    """Test with 1000 cents: 5% of 1000 is 50."""
    assert tax(1000) == 50

def test_tax_negative():
    """Test with negative cents: -100 * 5 // 100 = -5."""
    assert tax(-100) == -5

def test_tax_1():
    """Test with 1 cent: 1 * 5 // 100 = 0."""
    assert tax(1) == 0

def test_tax_2():
    """Test with 2 cents: 2 * 5 // 100 = 0."""
    assert tax(2) == 0

def test_tax_19():
    """Test with 19 cents: 19 * 5 // 100 = 95 // 100 = 0."""
    assert tax(19) == 0

def test_tax_20():
    """Test with 20 cents: 20 * 5 // 100 = 100 // 100 = 1."""
    assert tax(20) == 1

def test_tax_large_value():
    """Test with a large value: 1000000 cents * 5 // 100 = 50000."""
    assert tax(1000000) == 50000

def test_tax_returns_int():
    """Test that the return type is int."""
    result = tax(100)
    assert isinstance(result, int)

def test_tax_with_rate_5_percent():
    """Verify the calculation uses RATE=5 (5 percent)."""
    assert tax(1000) == 50
    assert tax(500) == 25
    assert tax(250) == 12
