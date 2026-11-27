import pytest
from subject import cap as target

def test_example_1():
    assert target(12) == 10

def test_normal_return_contract():
    assert isinstance(target(n=2, ceiling=2), int)

def test_boundary_return_contract():
    assert isinstance(target(n=0, ceiling=0), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
