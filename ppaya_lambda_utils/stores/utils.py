from decimal import Decimal
from enum import Enum
from typing import Any, Dict


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
    else:
        result = val
    return result
