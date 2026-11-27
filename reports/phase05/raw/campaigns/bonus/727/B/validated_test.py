import pytest
from subject import bonus as target

def test_example_1():
    assert target(3) == 4

def test_normal_return_contract():
    assert isinstance(target(n=2, enabled=True), int)

def test_boundary_return_contract():
    assert isinstance(target(n=0, enabled=False), int)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)
