import pytest
from subject import bonus

def test_bonus_example_1():
    assert bonus(3) == 4

def test_bonus_negative_raises_value_error():
    with pytest.raises(ValueError):
        bonus(-1)

def test_bonus_zero_enabled():
    assert bonus(0, enabled=True) == 0

def test_bonus_one_enabled():
    assert bonus(1, enabled=True) == 1

def test_bonus_two_enabled():
    assert bonus(2, enabled=True) == 3

def test_bonus_two_disabled():
    assert bonus(2, enabled=False) == 2

def test_bonus_three_enabled():
    assert bonus(3, enabled=True) == 4

def test_bonus_three_disabled():
    assert bonus(3, enabled=False) == 3

def test_bonus_negative_one_raises():
    with pytest.raises(ValueError):
        bonus(-1, enabled=True)





def test_bonus_large_number_enabled():
    assert bonus(100, enabled=True) == 101

def test_bonus_large_number_disabled():
    assert bonus(100, enabled=False) == 100
