from subject import page_count
import pytest

def test_example_1():
    assert page_count(9) == 1

def test_boundary_zero_items():
    assert page_count(0) == 0

def test_boundary_one_item():
    assert page_count(1) == 1

def test_boundary_page_size_items():
    assert page_count(10) == 1

def test_boundary_page_size_plus_one():
    assert page_count(11) == 2

def test_two_full_pages():
    assert page_count(20) == 2

def test_two_full_pages_plus_one():
    assert page_count(21) == 3
