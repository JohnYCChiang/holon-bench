import pytest
from mylib.math_utils import add_numbers


def test_add_integers():
    assert add_numbers(1, 2) == 3.0


def test_add_floats():
    assert add_numbers(1.5, 2.5) == 4.0


def test_add_mixed():
    assert add_numbers(1, 2.5) == 3.5


def test_return_type_is_float():
    result = add_numbers(2, 3)
    assert isinstance(result, float)
