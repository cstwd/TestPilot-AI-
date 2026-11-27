import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('tariff')
_tp_m.__file__ = 'tariff.py'
_tp_sys.modules['tariff'] = _tp_m
exec(compile('BASE = 5\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from tariff import BASE
from subject import freight

def test_freight_example():
    assert freight(3) == 8

def test_freight_boundary_zero():
    assert freight(0) == BASE

def test_freight_missing_argument():
    with pytest.raises(TypeError):
        freight()

def test_freight_keyword_argument():
    assert freight(units=2) == BASE + 2
