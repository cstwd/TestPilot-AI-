import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('policy')
_tp_m.__file__ = 'policy.py'
_tp_sys.modules['policy'] = _tp_m
exec(compile('def allowable(value):\n    return value >= 0\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import invoice as target

def test_example_1():
    assert target([4, -2, 3], 2) == 5

def test_normal_return_contract():
    assert isinstance(target(values=[1], discount=2), int)

def test_boundary_return_contract():
    assert isinstance(target(values=[], discount=0), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
