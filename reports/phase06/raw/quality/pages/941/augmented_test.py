import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('limits')
_tp_m.__file__ = 'limits.py'
_tp_sys.modules['limits'] = _tp_m
exec(compile('PAGE_SIZE = 10\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import page_count
from limits import PAGE_SIZE

def test_page_count_doctest_example():
    assert page_count(9) == 1







def test_page_count_one_over_one_page():
    assert page_count(PAGE_SIZE + 1) == 2




def test_page_count_two_pages_plus_one():
    assert page_count(2 * PAGE_SIZE + 1) == 3




def test_page_count_large_multiple_plus_one():
    assert page_count(100 * PAGE_SIZE + 1) == 101

def test_page_count_negative_items():
    assert page_count(-1) == 0

def test_page_count_missing_argument_raises():
    with pytest.raises(TypeError):
        page_count()

def test_page_count_extra_argument_raises():
    with pytest.raises(TypeError):
        page_count(items=2, _testpilot_unknown=None)
