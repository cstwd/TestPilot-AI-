import pytest
from subject import prefix_length

def test_prefix_length_empty_list():
    """Test that an empty list returns 0."""
    assert prefix_length([]) == 0

def test_prefix_length_no_none():
    """Test that a list with no None values returns the full length."""
    assert prefix_length([1, 2, 3, 4]) == 4

def test_prefix_length_none_at_start():
    """Test that a list starting with None returns 0."""
    assert prefix_length([None, 1, 2]) == 0

def test_prefix_length_none_at_end():
    """Test that a list with None at the end returns the count of non-None values."""
    assert prefix_length([1, 2, 3, None]) == 3

def test_prefix_length_none_in_middle():
    """Test that a list with None in the middle returns the count before None."""
    assert prefix_length([1, 2, None, 4, 5]) == 2

def test_prefix_length_single_non_none():
    """Test that a single non-None element returns 1."""
    assert prefix_length([42]) == 1

def test_prefix_length_single_none():
    """Test that a single None element returns 0."""
    assert prefix_length([None]) == 0

def test_prefix_length_all_none():
    """Test that a list with all None values returns 0."""
    assert prefix_length([None, None, None]) == 0

def test_prefix_length_mixed_types():
    """Test that the function works with mixed types before None."""
    assert prefix_length([1, 'two', 3.0, None, 4]) == 3

def test_prefix_length_zero_values():
    """Test that zero values are counted correctly."""
    assert prefix_length([0, 0, None, 1]) == 2

def test_prefix_length_false_values():
    """Test that False values are counted correctly (not treated as None)."""
    assert prefix_length([False, False, None, True]) == 2

def test_prefix_length_empty_strings():
    """Test that empty strings are counted correctly."""
    assert prefix_length(['', '', None, 'a']) == 2

def test_prefix_length_none_only_after_prefix():
    """Test that multiple Nones after the prefix are ignored."""
    assert prefix_length([1, 2, None, None, None]) == 2
