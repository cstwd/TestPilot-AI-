from subject import tier

def test_example_1():
    assert tier(120) == 'gold'

def test_boundary_gold_lower():
    assert tier(100) == 'gold'

def test_boundary_gold_above():
    assert tier(101) == 'gold'

def test_boundary_silver_upper():
    assert tier(99) == 'silver'

def test_boundary_silver_lower():
    assert tier(50) == 'silver'

def test_boundary_silver_above():
    assert tier(51) == 'silver'

def test_boundary_basic_upper():
    assert tier(49) == 'basic'

def test_boundary_zero():
    assert tier(0) == 'basic'

def test_negative_points():
    assert tier(-1) == 'basic'
