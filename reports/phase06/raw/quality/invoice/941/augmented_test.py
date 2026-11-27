import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('def allowable(value):\n    return value >= 0\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import invoice

def test_example_1():
    assert invoice([4, -2, 3], 2) == 5

def test_empty_values_with_discount():
    assert invoice([], 2) == 0

def test_single_value_no_discount():
    assert invoice([1], 0) == 1

def test_discount_exceeds_total():
    assert invoice([1], 2) == 0

def test_negative_values_ignored():
    assert invoice([-1, -2, -3], 0) == 0

def test_mixed_values():
    assert invoice([5, -1, 3, -2, 4], 1) == 11

def test_zero_value():
    assert invoice([0], 0) == 0

def test_large_values():
    assert invoice([1000, 2000, 3000], 500) == 5500

def test_default_discount():
    assert invoice([10, 20, 30]) == 60

def test_all_negative_values():
    assert invoice([-5, -10, -15], 0) == 0

def test_discount_equals_total():
    assert invoice([10, 20], 30) == 0

def test_single_negative_value():
    assert invoice([-1], 0) == 0

def test_float_values():
    assert invoice([1.5, 2.5, -0.5], 1) == 3

def test_zero_discount():
    assert invoice([5, 10, 15], 0) == 30

def test_large_discount():
    assert invoice([100], 1000) == 0

def test_multiple_zero_values():
    assert invoice([0, 0, 0], 0) == 0

def test_positive_and_negative_pairs():
    assert invoice([1, -1, 2, -2, 3, -3], 0) == 6

def test_single_large_value():
    assert invoice([1000000], 0) == 1000000

def test_discount_as_float():
    assert invoice([10, 20], 5.5) == 24.5

def test_values_with_zeros_and_negatives():
    assert invoice([0, -1, 5, -2, 0, 3], 1) == 7
