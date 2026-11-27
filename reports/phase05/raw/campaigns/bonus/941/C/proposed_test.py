from subject import bonus
import pytest

def test_example_1():
    assert bonus(3) == 4

def test_negative_raises_valueerror():
    with pytest.raises(ValueError):
        bonus(-1)

def test_zero_enabled_true():
    assert bonus(n=0, enabled=True) == 0

def test_one_enabled_true():
    assert bonus(n=1, enabled=True) == 1

def test_two_enabled_true():
    assert bonus(n=2, enabled=True) == 3

def test_two_enabled_false():
    assert bonus(n=2, enabled=False) == 2

def test_three_enabled_true():
    assert bonus(n=3, enabled=True) == 4

def test_three_enabled_false():
    assert bonus(n=3, enabled=False) == 3

def test_negative_one_raises_valueerror():
    with pytest.raises(ValueError):
        bonus(n=-1, enabled=True)
