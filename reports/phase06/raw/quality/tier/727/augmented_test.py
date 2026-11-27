import pytest
from subject import tier

def test_tier_gold_above_threshold():
    assert tier(120) == 'gold'

def test_tier_gold_at_threshold():
    assert tier(100) == 'gold'

def test_tier_silver_above_threshold():
    assert tier(51) == 'silver'

def test_tier_silver_at_threshold():
    assert tier(50) == 'silver'

def test_tier_basic_below_silver_threshold():
    assert tier(49) == 'basic'

def test_tier_basic_zero_points():
    assert tier(0) == 'basic'

def test_tier_basic_negative_points():
    assert tier(-1) == 'basic'

def test_tier_gold_just_above_threshold():
    assert tier(101) == 'gold'

def test_tier_silver_just_below_gold_threshold():
    assert tier(99) == 'silver'
