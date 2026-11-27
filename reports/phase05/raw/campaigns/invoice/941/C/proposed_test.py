from subject import invoice

def test_example_1():
    assert invoice([4, -2, 3], 2) == 5

def test_empty_values_with_discount():
    assert invoice([], 2) == 0

def test_single_value_no_discount():
    assert invoice([1], 0) == 1

def test_single_value_discount_exceeds_total():
    assert invoice([1], 2) == 0
