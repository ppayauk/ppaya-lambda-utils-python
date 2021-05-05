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
