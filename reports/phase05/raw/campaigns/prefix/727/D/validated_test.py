from subject import prefix_length

def test_example_1():
    assert prefix_length([4, None, 2]) == 1

def test_empty_list():
    assert prefix_length([]) == 0

def test_no_none():
    assert prefix_length([1]) == 1

def test_all_none():
    assert prefix_length([None]) == 0

def test_none_at_start():
    assert prefix_length([None, 1, 2]) == 0

def test_multiple_values_before_none():
    assert prefix_length([1, 2, 3, None, 4]) == 3

def test_none_at_end():
    assert prefix_length([1, 2, 3, None]) == 3
