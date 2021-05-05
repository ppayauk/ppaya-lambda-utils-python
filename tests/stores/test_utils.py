import pytest

from ppaya_lambda_utils.stores.utils import (
    normalise_key, to_camel_case, dict_to_camel_case)


@pytest.mark.parametrize(
    'val, expected', [
        ('name', 'name'),
        ('NaMe', 'name'),
        ('Some Name', 'somename'),
    ]
)
def test_normalise_key(val, expected) -> None:
    assert normalise_key(val) == expected


@pytest.mark.parametrize(
    'val, expected', [
        ('name', 'name'),
        ('some_name', 'someName'),
        ('some_long_name', 'someLongName'),
    ]
)
def test_to_camel_case(val, expected) -> None:
    assert to_camel_case(val) == expected


@pytest.mark.parametrize(
    'val, expected', [
        ({}, {}),
        ({'some_key': 'some value'}, {'someKey': 'some value'}),
        ({'my_key': 'a', 'other_key': 'b'}, {'myKey': 'a', 'otherKey': 'b'}),
    ]
)
def test_dict_to_camel_case(val, expected) -> None:
    assert dict_to_camel_case(val) == expected
