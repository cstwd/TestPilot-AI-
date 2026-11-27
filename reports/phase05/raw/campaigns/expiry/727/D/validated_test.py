from subject import expired

def test_expired_example_1():
    assert expired(31) is True

def test_expired_at_limit():
    assert expired(30) is False

def test_expired_just_above_limit():
    assert expired(31, 30) is True

def test_expired_below_limit():
    assert expired(29, 30) is False

def test_expired_custom_limit():
    assert expired(10, 5) is True

def test_expired_custom_limit_not_expired():
    assert expired(4, 5) is False

def test_expired_zero_age():
    assert expired(0) is False

def test_expired_zero_limit():
    assert expired(1, 0) is True

def test_expired_negative_age():
    assert expired(-1) is False

def test_expired_negative_limit():
    assert expired(0, -1) is True
