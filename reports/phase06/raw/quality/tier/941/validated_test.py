from subject import tier

def test_tier_gold_above_threshold():
    assert tier(120) == 'gold'

def test_tier_gold_at_threshold():
    assert tier(100) == 'gold'

def test_tier_silver_above_threshold():
    assert tier(51) == 'silver'

def test_tier_silver_at_threshold():
    assert tier(50) == 'silver'

def test_tier_basic_below_silver():
    assert tier(49) == 'basic'

def test_tier_basic_at_zero():
    assert tier(0) == 'basic'

def test_tier_gold_above_100():
    assert tier(101) == 'gold'

def test_tier_silver_below_gold():
    assert tier(99) == 'silver'








