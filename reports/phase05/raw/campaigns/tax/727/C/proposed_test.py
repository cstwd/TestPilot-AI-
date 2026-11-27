from subject import tax

def test_example_1():
    assert tax(100) == 5

def test_boundary_zero():
    assert tax(0) == 0

def test_missing_argument():
    with pytest.raises(TypeError):
        tax()
