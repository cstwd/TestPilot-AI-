from subject import cap

def test_cap_returns_n_when_less_than_ceiling():
    assert cap(5, 10) == 5

def test_cap_returns_ceiling_when_n_greater():
    assert cap(12, 10) == 10

def test_cap_returns_ceiling_when_n_equals_ceiling():
    assert cap(10, 10) == 10

def test_cap_with_default_ceiling():
    assert cap(12) == 10

def test_cap_with_zero_n():
    assert cap(0, 10) == 0

def test_cap_with_zero_ceiling():
    assert cap(5, 0) == 0

def test_cap_with_negative_n():
    assert cap(-5, 10) == -5

def test_cap_with_negative_ceiling():
    assert cap(5, -10) == -10

def test_cap_with_both_negative():
    assert cap(-5, -10) == -10

def test_cap_with_large_values():
    assert cap(1000000, 500000) == 500000

def test_cap_with_same_large_values():
    assert cap(1000000, 1000000) == 1000000

def test_cap_with_keyword_arguments():
    assert cap(n=12, ceiling=10) == 10

def test_cap_with_mixed_keyword_arguments():
    assert cap(12, ceiling=10) == 10

def test_cap_with_ceiling_as_keyword():
    assert cap(n=12, ceiling=10) == 10

def test_cap_doctest_example():
    assert cap(12) == 10
