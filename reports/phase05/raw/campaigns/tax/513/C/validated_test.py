import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('RATE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

from subject import tax

def test_example_1():
    assert tax(100) == 5

def test_boundary_zero():
    assert tax(0) == 0




