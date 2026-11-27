import pytest
from subject import cap

def test_cap_returns_ceiling_when_n_exceeds_ceiling():
    assert cap(12) == 10

def test_cap_returns_n_when_n_is_less_than_ceiling():
    assert cap(5) == 5

def test_cap_returns_ceiling_when_n_equals_ceiling():
    assert cap(10) == 10

def test_cap_with_custom_ceiling():
    assert cap(15, 20) == 15
    assert cap(25, 20) == 20

def test_cap_with_zero_n():
    assert cap(0) == 0

def test_cap_with_zero_ceiling():
    assert cap(5, 0) == 0

def test_cap_with_negative_n():
    assert cap(-5) == -5

def test_cap_with_negative_ceiling():
    assert cap(5, -10) == -10

def test_cap_with_negative_n_and_ceiling():
    assert cap(-5, -10) == -10

def test_cap_with_large_values():
    assert cap(1000000, 500000) == 500000
    assert cap(400000, 500000) == 400000

def test_cap_with_keyword_arguments():
    assert cap(n=12, ceiling=10) == 10
    assert cap(n=5, ceiling=10) == 5

def test_cap_returns_int_type():
    result = cap(12)
    assert isinstance(result, int)

def test_cap_boundary_equal_values():
    assert cap(n=2, ceiling=2) == 2

def test_cap_boundary_zero_n_positive_ceiling():
    assert cap(n=0, ceiling=2) == 0

def test_cap_boundary_positive_n_zero_ceiling():
    assert cap(n=2, ceiling=0) == 0


def test_mutation_9bd8518be37365d7():
    from subject import cap
    assert cap(0, 0) == 0
