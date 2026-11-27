from subject import expired

def test_expired_at_limit_is_false():
    """An item is not expired at exactly its age limit."""
    assert expired(30) is False

def test_expired_beyond_limit_is_true():
    """An item is expired when age exceeds the limit."""
    assert expired(31) is True

def test_expired_with_custom_limit_at_boundary():
    """Custom limit: age equal to limit is not expired."""
    assert expired(age=2, limit=2) is False

def test_expired_with_custom_limit_beyond_boundary():
    """Custom limit: age greater than limit is expired."""
    assert expired(age=3, limit=2) is True

def test_expired_zero_age_zero_limit():
    """Zero age with zero limit is not expired."""
    assert expired(age=0, limit=0) is False

def test_expired_zero_age_positive_limit():
    """Zero age with positive limit is not expired."""
    assert expired(age=0, limit=2) is False

def test_expired_positive_age_zero_limit():
    """Positive age with zero limit is expired."""
    assert expired(age=1, limit=0) is True

def test_expired_negative_age():
    """Negative age with default limit is not expired."""
    assert expired(-1) is False

def test_expired_negative_age_negative_limit():
    """Negative age with negative limit: -1 > -5 is True."""
    assert expired(age=-1, limit=-5) is True

def test_expired_negative_age_equal_limit():
    """Negative age equal to negative limit is not expired."""
    assert expired(age=-5, limit=-5) is False

def test_expired_large_values():
    """Large age beyond large limit is expired."""
    assert expired(age=1000000, limit=999999) is True

def test_expired_large_values_at_boundary():
    """Large age equal to large limit is not expired."""
    assert expired(age=1000000, limit=1000000) is False
