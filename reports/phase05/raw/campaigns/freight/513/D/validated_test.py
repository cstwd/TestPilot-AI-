import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('tariff')
_tp_m.__file__ = 'tariff.py'
_tp_sys.modules['tariff'] = _tp_m
exec(compile('BASE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

from subject import freight

def test_example_1():
    assert freight(3) == 8

def test_boundary_zero():
    assert freight(0) == 5

def test_units_two():
    assert freight(2) == 7
