from subject import freight

def test_example_1():
    assert freight(3) == 8

def test_boundary_zero():
    assert freight(0) == 5

def test_units_two():
    assert freight(2) == 7
