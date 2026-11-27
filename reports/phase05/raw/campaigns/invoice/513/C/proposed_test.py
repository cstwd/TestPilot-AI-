from subject import invoice

def test_example_1():
    assert invoice([4, -2, 3], 2) == 5

def test_empty_values_with_discount():
    assert invoice([], 2) == 0

def test_single_value_no_discount():
    assert invoice([1], 0) == 1

def test_single_value_with_discount_exceeding_total():
    assert invoice([1], 2) == 0

def test_all_negative_values():
    assert invoice([-1, -2, -3], 0) == 0

def test_zero_values():
    assert invoice([0, 0, 0], 0) == 0

def test_mixed_values_no_discount():
    assert invoice([5, -1, 3, -2, 4], 0) == 12

def test_discount_equals_total():
    assert invoice([5, 3], 8) == 0

def test_discount_less_than_total():
    assert invoice([5, 3], 5) == 3
