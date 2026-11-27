import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('tariff')
_tp_m.__file__ = 'tariff.py'
_tp_sys.modules['tariff'] = _tp_m
exec(compile('BASE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

from subject import freight

def test_freight_doctest_example():
    assert freight(3) == 8

def test_freight_zero_units():
    assert freight(0) == 5

def test_freight_positive_units():
    assert freight(1) == 6

def test_freight_negative_units():
    assert freight(-2) == 3
