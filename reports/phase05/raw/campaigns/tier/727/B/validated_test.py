import pytest
from subject import tier as target

def test_example_1():
    assert target(120) == 'gold'

def test_normal_return_contract():
    assert isinstance(target(points=2), str)

def test_boundary_return_contract():
    assert isinstance(target(points=0), str)

def test_invalid_keyword():
    with pytest.raises(TypeError):
        target(_testpilot_unexpected=None)

def test_property_return_contract():
    hypothesis = pytest.importorskip('hypothesis')
    from hypothesis import strategies as st

    @hypothesis.settings(max_examples=12, database=None, deadline=None)
    @hypothesis.given(st.integers(min_value=-100, max_value=100))
    def check(x):
        assert isinstance(target(points=x), str)
    check()
