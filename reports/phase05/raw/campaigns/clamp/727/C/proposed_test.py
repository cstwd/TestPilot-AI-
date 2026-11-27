from subject import cap

def test_example_1():
    assert cap(12) == 10

def test_n_less_than_ceiling():
    assert cap(5, 10) == 5

def test_n_equal_to_ceiling():
    assert cap(10, 10) == 10

def test_n_greater_than_ceiling():
    assert cap(15, 10) == 10

def test_boundary_n_zero_ceiling_positive():
    assert cap(0, 2) == 0

def test_boundary_n_positive_ceiling_zero():
    assert cap(2, 0) == 0

def test_boundary_n_zero_ceiling_zero():
    assert cap(0, 0) == 0

def test_custom_ceiling():
    assert cap(7, 5) == 5

def test_negative_n():
    assert cap(-3, 10) == -3

def test_negative_ceiling():
    assert cap(5, -1) == -1
