from subject import first

def test_example_1():
    assert first([8]) == 8

def test_empty_list_returns_zero():
    assert first([]) == 0

def test_empty_list_with_fallback_returns_zero():
    assert first([], 2) == 0

def test_single_item_with_fallback():
    assert first([1], 0) == 1

def test_single_item_with_fallback_two():
    assert first([1], 2) == 1
