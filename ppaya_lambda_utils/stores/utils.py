import dataclasses
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum, EnumMeta
from typing import Any, Dict, get_args, List, Tuple, Type


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
    result: Dict[str, Any] = {}
    for k, v in snake_dict.items():
        if isinstance(v, list):
            val = []
            for x in v:
                if isinstance(x, dict):
                    val.append(dict_to_camel_case(x))
                else:
                    val.append(x)
            result[to_camel_case(k)] = val
        elif isinstance(v, dict):
            result[to_camel_case(k)] = dict_to_camel_case(v)
        else:
            result[to_camel_case(k)] = v
    return result


def to_dynamodb_compatible_type(val: Any) -> Any:
    """
    Convert a value to a type compatible with dynamodb datatypes.
    """
    result: Any = None

    if isinstance(val, (str, int)):
        # Return early for most common case
        return val

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
    elif isinstance(val, list):
        result = [to_dynamodb_compatible_type(x) for x in val]
    elif isinstance(val, dict):
        result = {
            to_camel_case(k): to_dynamodb_compatible_type(v)
            for k, v in val.items()}
    elif dataclasses.is_dataclass(val):
        result = {
            to_camel_case(k): to_dynamodb_compatible_type(v)
            for k, v in dataclasses.asdict(val).items()}
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
        if str in type_args or to_type == str:
            result = val
        elif is_datetime_type(to_type, type_args):
            result = datetime.fromisoformat(val.replace('Z', '+00:00'))
        elif is_date_type(to_type, type_args):
            result = date.fromisoformat(val)
        elif EnumMeta in [type(x) for x in type_args]:
            result = [x for x in type_args if is_enum_type(x)][0][val]
        elif is_enum_type(to_type):
            result = to_type[val]

    return result


def is_type(t: Type, t_args: Tuple, names: List[str]) -> bool:
    for x in t_args:
        if x.__name__ in names:
            return True

    if not t_args:
        if t.__name__ in names:
            return True

    return False


def is_date_type(t: Type, t_args: Tuple) -> bool:
    return is_type(t, t_args, ['date', 'FakeDateMeta'])


def is_datetime_type(t: Type, t_args: Tuple) -> bool:
    return is_type(t, t_args, ['datetime', 'FakeDatetimeMeta'])


def is_enum_type(T):
    return type(T) == EnumMeta
