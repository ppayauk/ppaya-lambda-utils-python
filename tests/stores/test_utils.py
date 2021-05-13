from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

import pytest

from ppaya_lambda_utils.stores.utils import (
    normalise_key, to_camel_case, dict_to_camel_case,
    to_dynamodb_compatible_type, graphql_value_to_typed)


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


class MyEnum(Enum):
    OK = 1


@pytest.mark.parametrize(
    'val, expected', [
        ('string', 'string'),
        (1, 1),
        (2.5, Decimal('2.5')),
        (MyEnum.OK, 'OK'),
        (date(2021, 1, 1), '2021-01-01'),
        (datetime(2021, 1, 1, 13, 30), '2021-01-01T13:30:00+00:00'),
        (datetime(2021, 1, 1, 13, 30, tzinfo=timezone.utc), '2021-01-01T13:30:00+00:00'),
    ]
)
def test_to_dynamodb_compatible_type(val, expected) -> None:
    assert to_dynamodb_compatible_type(val) == expected


@pytest.mark.parametrize(
    'val, to_type, expected', [
        ('string', str, 'string'),
        ('string', Optional[str], 'string'),
        (1, int, 1),
        (1, Union[int, float], 1),
        ('OK', MyEnum, MyEnum.OK),
        ('OK', Optional[MyEnum], MyEnum.OK),
        ('2021-01-01', date, date(2021, 1, 1)),
        ('2021-01-01T13:30:00+00:00', datetime, datetime(2021, 1, 1, 13, 30, tzinfo=timezone.utc)),
        ('2021-01-01T13:30:00Z', datetime, datetime(2021, 1, 1, 13, 30, tzinfo=timezone.utc)),
    ]
)
def test_graphql_value_to_typed(val, to_type, expected) -> None:
    assert graphql_value_to_typed(val, to_type) == expected
