import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('limits')
_tp_m.__file__ = 'limits.py'
_tp_sys.modules['limits'] = _tp_m
exec(compile('PAGE_SIZE = 10\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

from subject import page_count
import pytest

def test_example_1():
    assert page_count(9) == 1




def test_boundary_one_item():
    assert page_count(1) == 1




def test_boundary_page_size_plus_one():
    assert page_count(11) == 2




def test_two_full_pages_plus_one():
    assert page_count(21) == 3
