from subject import first

def test_example_1():
    assert first([8]) == 8

def test_empty_list_returns_zero():
    assert first([]) == 0

def test_empty_list_with_fallback_returns_zero():
    assert first([], fallback=2) == 0

def test_non_empty_list_returns_first_item():
    assert first([1], fallback=2) == 1

def test_non_empty_list_with_zero_fallback():
    assert first([1], fallback=0) == 1
