import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('limits')
_tp_m.__file__ = 'limits.py'
_tp_sys.modules['limits'] = _tp_m
exec(compile('PAGE_SIZE = 10\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import page_count
from limits import PAGE_SIZE





def test_page_count_one_item():
    """One item should require one page."""
    assert page_count(1) == 1





def test_page_count_one_more_than_one_page():
    """PAGE_SIZE + 1 items should require two pages."""
    assert page_count(PAGE_SIZE + 1) == 2





def test_page_count_multiple_full_pages_plus_one():
    """2 * PAGE_SIZE + 1 items should require 3 pages."""
    assert page_count(2 * PAGE_SIZE + 1) == 3

def test_page_count_large_number():
    """A large number of items should compute correct page count."""
    items = 1000
    assert page_count(items) == items // PAGE_SIZE + 1





