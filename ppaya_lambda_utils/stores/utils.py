from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum, EnumMeta
from typing import Any, Dict, get_args, Type


def normalise_key(val: str) -> str:
    """
    Normalise a string key to be case and white space insensitive.

    eg "Some  NaMe" > "somename"
    """
    return val.replace(' ', '').lower()


def to_camel_case(snake_str: str) -> str:
    """
    Covert a string from snake case to camel case eg.
    to_camel_case('snake_case') ->  'snakeCase'
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dict_to_camel_case(snake_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all keys in a dictionary from snake case to camel case.
    """
    return {
        to_camel_case(k): v for k, v in snake_dict.items()}


def to_dynamodb_compatible_type(val: Any) -> Any:
    """
    Convert a value to a type compatible with dynamodb datatypes.
    """
    result: Any = None
    if isinstance(val, Enum):
        result = val.name
    elif isinstance(val, float):
        result = Decimal(str(val))
    elif isinstance(val, datetime):
        if val.tzinfo:
            result = val.isoformat()
        else:
            result = val.astimezone(timezone.utc).isoformat()
    elif isinstance(val, date):
        result = val.isoformat()
    else:
        result = val
    return result


def graphql_value_to_typed(val: Any, to_type: Type) -> Any:
    """
    Converts a value from a GraphQL resolver into a typed python value.

    Specifically:
    - Javascript / GraphQL format date and datetime strings are parsed to python values
    - Strings with a `to_type` of an Enum will be parsed to the Enum value.
    """
    result = val
    type_args = get_args(to_type)
    if isinstance(val, str):
        if datetime in type_args or to_type == datetime:
            result = datetime.fromisoformat(val.replace('Z', '+00:00'))
        elif date in type_args or to_type == date:
            result = date.fromisoformat(val)
        elif EnumMeta in [type(x) for x in type_args]:
            result = [x for x in type_args if is_enum_type(x)][0][val]
        elif is_enum_type(to_type):
            result = to_type[val]
    return result


def is_enum_type(T):
    return type(T) == EnumMeta
