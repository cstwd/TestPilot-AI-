from subject import cap

def test_cap():
    assert cap(12) == 10
    assert cap(10) == 10
    assert cap(15) == 15
    assert cap(0) == 0
    assert cap(2) == 2
    assert cap(100) == 100
    assert cap(101) == 101
    assert cap(-10) == -10
    assert cap(-100) == -100
    assert cap(-101) == -101
