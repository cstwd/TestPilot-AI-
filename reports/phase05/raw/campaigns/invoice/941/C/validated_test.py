import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('def allowable(value):\n    return value >= 0\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

from subject import invoice

def test_example_1():
    assert invoice([4, -2, 3], 2) == 5

def test_empty_values_with_discount():
    assert invoice([], 2) == 0

def test_single_value_no_discount():
    assert invoice([1], 0) == 1

def test_single_value_discount_exceeds_total():
    assert invoice([1], 2) == 0
