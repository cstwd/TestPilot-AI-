from subject import cap

def test_example_1():
    assert cap(12) == 10

def test_n_less_than_ceiling():
    assert cap(5, ceiling=10) == 5

def test_n_equal_to_ceiling():
    assert cap(10, ceiling=10) == 10

def test_n_zero_ceiling_positive():
    assert cap(0, ceiling=2) == 0

def test_n_positive_ceiling_zero():
    assert cap(2, ceiling=0) == 0

def test_n_equal_ceiling_equal():
    assert cap(2, ceiling=2) == 2

def test_negative_n():
    assert cap(-5, ceiling=10) == -5
