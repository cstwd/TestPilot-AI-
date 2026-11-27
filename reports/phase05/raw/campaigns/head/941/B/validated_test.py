import pytest
from subject import first as target

def test_example_1():
    assert target([8]) == 8

def test_normal_return_contract():
    assert isinstance(target(items=[1], fallback=2), int)

def test_boundary_return_contract():
    assert isinstance(target(items=[], fallback=0), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
