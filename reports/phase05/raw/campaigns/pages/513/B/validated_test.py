import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('limits')
_tp_m.__file__ = 'limits.py'
_tp_sys.modules['limits'] = _tp_m
exec(compile('PAGE_SIZE = 10\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import page_count as target

def test_example_1():
    assert target(9) == 1

def test_normal_return_contract():
    assert isinstance(target(items=2), int)

def test_boundary_return_contract():
    assert isinstance(target(items=0), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)

def test_property_return_contract():
    hypothesis = pytest.importorskip('hypothesis')
    from hypothesis import strategies as st

    @hypothesis.settings(max_examples=12, database=None, deadline=None)
    @hypothesis.given(st.integers(min_value=-100, max_value=100))
    def check(x):
        assert isinstance(target(items=x), int)
    check()
