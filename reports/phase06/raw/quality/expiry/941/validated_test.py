from subject import expired

def test_expired_true_when_age_exceeds_limit():
    assert expired(31) is True

def test_expired_false_when_age_equals_limit():
    assert expired(30) is False

def test_expired_false_when_age_below_limit():
    assert expired(29) is False

def test_expired_custom_limit():
    assert expired(5, limit=3) is True
    assert expired(3, limit=3) is False
    assert expired(2, limit=3) is False

def test_expired_zero_age():
    assert expired(0) is False

def test_expired_zero_limit():
    assert expired(1, limit=0) is True
    assert expired(0, limit=0) is False

def test_expired_negative_age():
    assert expired(-1) is False

def test_expired_negative_limit():
    assert expired(0, limit=-1) is True

def test_expired_large_values():
    assert expired(100, limit=99) is True
    assert expired(99, limit=99) is False

def test_expired_keyword_arguments():
    assert expired(age=31) is True
    assert expired(age=31, limit=30) is True
    assert expired(age=30, limit=30) is False
