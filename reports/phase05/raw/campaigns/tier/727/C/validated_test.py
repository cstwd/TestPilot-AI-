from subject import tier

def test_example_1():
    assert tier(120) == 'gold'

def test_boundary_gold():
    assert tier(100) == 'gold'

def test_boundary_silver():
    assert tier(50) == 'silver'

def test_below_silver():
    assert tier(49) == 'basic'

def test_zero_points():
    assert tier(0) == 'basic'

def test_negative_points():
    assert tier(-1) == 'basic'




def test_just_above_gold():
    assert tier(101) == 'gold'

def test_just_above_silver():
    assert tier(51) == 'silver'
