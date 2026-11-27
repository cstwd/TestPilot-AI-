from subject import cap

def test_cap_returns_ceiling_when_n_exceeds_ceiling():
    assert cap(12) == 10

def test_cap_returns_n_when_n_is_less_than_ceiling():
    assert cap(5) == 5

def test_cap_returns_ceiling_when_n_equals_ceiling():
    assert cap(10) == 10

def test_cap_with_custom_ceiling():
    assert cap(15, ceiling=20) == 15
    assert cap(25, ceiling=20) == 20

def test_cap_with_zero_n():
    assert cap(0) == 0

def test_cap_with_zero_ceiling():
    assert cap(5, ceiling=0) == 0

def test_cap_with_negative_n():
    assert cap(-5) == -5

def test_cap_with_negative_ceiling():
    assert cap(5, ceiling=-1) == -1




def test_cap_with_large_values():
    assert cap(1000000) == 10
    assert cap(1000000, ceiling=2000000) == 1000000
