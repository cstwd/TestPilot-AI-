import pytest
from subject import expired as target

def test_example_1():
    assert target(31) == True

def test_normal_return_contract():
    assert isinstance(target(age=2, limit=2), bool)

def test_boundary_return_contract():
    assert isinstance(target(age=0, limit=0), bool)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
