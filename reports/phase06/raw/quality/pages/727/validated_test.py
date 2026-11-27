import sys as _tp_sys, types as _tp_types
_tp_m = _tp_types.ModuleType('limits')
_tp_m.__file__ = 'limits.py'
_tp_sys.modules['limits'] = _tp_m
exec(compile('PAGE_SIZE = 10\n', _tp_m.__file__, 'exec'), _tp_m.__dict__)

import pytest
from subject import page_count
from limits import PAGE_SIZE





def test_page_count_one_item_returns_one():
    """One item should require one page."""
    assert page_count(1) == 1





def test_page_count_one_more_than_page_size_returns_two():
    """One more than PAGE_SIZE items should require two pages."""
    assert page_count(PAGE_SIZE + 1) == 2

def test_page_count_nine_returns_one():
    """Nine items (less than PAGE_SIZE=10) should require one page."""
    assert page_count(9) == 1





def test_page_count_twenty_one_returns_three():
    """Twenty-one items (2 * PAGE_SIZE + 1) should require three pages."""
    assert page_count(2 * PAGE_SIZE + 1) == 3






def test_page_count_large_multiple_plus_one():
    """A large multiple of PAGE_SIZE plus one should return one more page."""
    n_pages = 100
    assert page_count(n_pages * PAGE_SIZE + 1) == n_pages + 1






def test_page_count_non_integer_raises():
    """Non-integer input should raise a TypeError."""
    with pytest.raises(TypeError):
        page_count('10')





