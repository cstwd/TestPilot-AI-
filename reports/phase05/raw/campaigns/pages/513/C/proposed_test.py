from subject import page_count

def test_example_1():
    assert page_count(9) == 1

def test_boundary_zero_items():
    assert page_count(0) == 0
