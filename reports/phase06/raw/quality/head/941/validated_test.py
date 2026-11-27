from subject import first

def test_first_returns_first_item():
    """Test that first returns the first item of a non-empty list."""
    result = first([8])
    assert result == 8

def test_first_returns_first_item_with_fallback():
    """Test that first returns the first item even when fallback is provided."""
    result = first([1], fallback=2)
    assert result == 1

def test_first_empty_list_returns_zero():
    """Test that first returns 0 for an empty list (actual behavior)."""
    result = first([], fallback=2)
    assert result == 0

def test_first_single_element_list():
    """Test that first returns the single element of a one-item list."""
    result = first([42])
    assert result == 42

def test_first_multiple_elements_returns_first():
    """Test that first returns only the first element, not others."""
    result = first([1, 2, 3, 4])
    assert result == 1

def test_first_with_zero_as_first_element():
    """Test that first correctly returns 0 when it is the first element."""
    result = first([0, 1, 2])
    assert result == 0

def test_first_with_negative_first_element():
    """Test that first correctly returns a negative number as first element."""
    result = first([-5, 3, 7])
    assert result == -5

def test_first_with_string_elements():
    """Test that first works with string elements."""
    result = first(['a', 'b', 'c'])
    assert result == 'a'

def test_first_with_none_as_first_element():
    """Test that first correctly returns None when it is the first element."""
    result = first([None, 1, 2])
    assert result is None

def test_first_with_fallback_zero():
    """Test that first with fallback=0 still returns first item for non-empty list."""
    result = first([1], fallback=0)
    assert result == 1

def test_first_empty_list_default_fallback():
    """Test that first returns 0 for empty list with default fallback."""
    result = first([])
    assert result == 0

def test_first_with_boolean_elements():
    """Test that first works with boolean elements."""
    result = first([True, False, True])
    assert result is True

def test_first_with_mixed_types():
    """Test that first returns the first element regardless of type."""
    result = first(['hello', 42, None])
    assert result == 'hello'

def test_first_with_large_list():
    """Test that first works correctly with a large list."""
    large_list = list(range(1000))
    result = first(large_list)
    assert result == 0

def test_first_with_float_elements():
    """Test that first works with float elements."""
    result = first([3.14, 2.71, 1.41])
    assert result == 3.14
