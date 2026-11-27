import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('RATE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from policy import RATE
from subject import tax

def test_tax_example_100():
    assert tax(100) == 5

def test_tax_zero():
    assert tax(0) == 0

def test_tax_below_one_hundred():
    assert tax(99) == 4

def test_tax_one_hundred():
    assert tax(100) == 5

def test_tax_large_value():
    assert tax(10000) == 500

def test_tax_negative_value():
    assert tax(-100) == -5

def test_tax_non_integer_string_raises():
    with pytest.raises(TypeError):
        tax('100')





def test_tax_none_raises():
    with pytest.raises(TypeError):
        tax(None)

def test_tax_missing_argument_raises():
    with pytest.raises(TypeError):
        tax()

def test_tax_returns_int_type():
    result = tax(100)
    assert isinstance(result, int)

def test_tax_rate_consistency():
    cents = 1234
    expected = cents * RATE // 100
    assert tax(cents) == expected

def test_tax_boundary_1():
    assert tax(1) == 0

def test_tax_boundary_19():
    assert tax(19) == 0

def test_tax_boundary_20():
    assert tax(20) == 1
