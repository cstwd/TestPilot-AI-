import pytest
from subject import prefix_length

def test_prefix_length_with_none_in_middle():
    """Test that prefix_length counts entries before the first None."""
    assert prefix_length([4, None, 2]) == 1

def test_prefix_length_with_no_none():
    """Test that prefix_length returns the full length when no None is present."""
    assert prefix_length([1, 2, 3]) == 3

def test_prefix_length_with_none_at_start():
    """Test that prefix_length returns 0 when the first element is None."""
    assert prefix_length([None, 1, 2]) == 0

def test_prefix_length_with_empty_list():
    """Test that prefix_length returns 0 for an empty list."""
    assert prefix_length([]) == 0

def test_prefix_length_with_single_non_none():
    """Test that prefix_length returns 1 for a single non-None element."""
    assert prefix_length([1]) == 1

def test_prefix_length_with_single_none():
    """Test that prefix_length returns 0 for a single None element."""
    assert prefix_length([None]) == 0

def test_prefix_length_with_multiple_nones():
    """Test that prefix_length stops at the first None even if there are more Nones."""
    assert prefix_length([1, None, None, 2]) == 1

def test_prefix_length_with_none_at_end():
    """Test that prefix_length counts all elements before a trailing None."""
    assert prefix_length([1, 2, 3, None]) == 3

def test_prefix_length_with_zero_values():
    """Test that prefix_length handles zero values correctly."""
    assert prefix_length([0, 0, None, 1]) == 2

def test_prefix_length_with_negative_values():
    """Test that prefix_length handles negative values correctly."""
    assert prefix_length([-1, -2, None, 1]) == 2

def test_prefix_length_with_strings():
    """Test that prefix_length works with string values."""
    assert prefix_length(['a', 'b', None, 'c']) == 2

def test_prefix_length_with_mixed_types():
    """Test that prefix_length works with mixed types before None."""
    assert prefix_length([1, 'a', None, 2]) == 2
