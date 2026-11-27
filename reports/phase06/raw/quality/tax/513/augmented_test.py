import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('RATE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import tax
from policy import RATE

def test_tax_doctest_example():
    assert tax(100) == 5

def test_tax_zero():
    assert tax(0) == 0

def test_tax_one():
    assert tax(1) == 0

def test_tax_ninety_nine():
    assert tax(99) == 4

def test_tax_one_hundred():
    assert tax(100) == 5

def test_tax_one_hundred_one():
    assert tax(101) == 5

def test_tax_uses_policy_rate():
    assert tax(100) == 100 * RATE // 100

def test_tax_is_integer():
    assert isinstance(tax(100), int)

def test_tax_negative():
    assert tax(-100) == -5

def test_tax_large_value():
    assert tax(1000000) == 50000

def test_tax_missing_argument():
    with pytest.raises(TypeError):
        tax()

def test_tax_wrong_type():
    with pytest.raises(TypeError):
        tax('100')




