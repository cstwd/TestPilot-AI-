from subject import expired

def test_expired_example():
    assert expired(31) is True

def test_expired_at_limit():
    assert expired(30) is False

def test_expired_just_above_limit():
    assert expired(31) is True

def test_expired_just_below_limit():
    assert expired(29) is False

def test_expired_zero_age():
    assert expired(0) is False

def test_expired_custom_limit():
    assert expired(5, 3) is True

def test_expired_custom_limit_equal():
    assert expired(3, 3) is False

def test_expired_custom_limit_below():
    assert expired(2, 3) is False

def test_expired_negative_age():
    assert expired(-1) is False

def test_expired_negative_limit():
    assert expired(0, -1) is True
