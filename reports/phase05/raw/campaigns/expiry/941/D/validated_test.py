from subject import expired

def test_expired_example():
    assert expired(31) is True

def test_expired_at_limit():
    assert expired(30) is False

def test_expired_below_limit():
    assert expired(29) is False

def test_expired_above_limit():
    assert expired(31) is True

def test_expired_custom_limit_at_limit():
    assert expired(2, limit=2) is False

def test_expired_custom_limit_above():
    assert expired(3, limit=2) is True




def test_expired_zero_age_zero_limit():
    assert expired(0, limit=0) is False

def test_expired_zero_age_positive_limit():
    assert expired(0, limit=2) is False

def test_expired_positive_age_zero_limit():
    assert expired(1, limit=0) is True

def test_expired_negative_age():
    assert expired(-1) is False
