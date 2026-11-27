import pytest
from subject import prefix_length as target

def test_example_1():
    assert target([4, None, 2]) == 1

def test_normal_return_contract():
    assert isinstance(target(values=[1]), int)

def test_boundary_return_contract():
    assert isinstance(target(values=[]), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
