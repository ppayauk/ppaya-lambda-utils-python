from abc import abstractmethod
from dataclasses import dataclass, asdict, fields
from enum import Enum
from typing import Any, Dict, List, Protocol, Tuple, Type

from ppaya_lambda_utils.stores.utils import to_camel_case, dict_to_camel_case


@dataclass
class AbstractInputData(Protocol):
    """
    A protocol / interface that all input data classes should implement for
    type checking purposes.
    """
    pass


class AbstracInputParser(Protocol):
    """
    An interface / protocol that all input parsers should implement.
    At PPAYA we have mostly standardised on a composite primary key
    ("PK" and "SK") and a global secondary index ("PK_GSI1", "SK_GSI1").

    This class reflects that standardisation and defines methods to derive
    the various keys based on the provided `input_data` instance.
    """
    input_data: AbstractInputData

    @abstractmethod
    def get_pk(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_sk(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_pk_gsi1(self) -> Tuple[bool, str]:
        raise NotImplementedError()

    @abstractmethod
    def get_sk_gsi1(self) -> Tuple[bool, str]:
        raise NotImplementedError()


def to_new_put_item(parser: AbstracInputParser) -> Dict[str, Any]:
    """
    Create an item dictionary to pass as an argument to boto3 dynamodb
    `table.put_item()`.

    DynamoDB data is mostly queried from GraphQL, so field names are converted
    to camel case for the sake of simplicity in resolvers.

    Usage::

        input_data = MyInput(field_1='a', field_2='b')
        paraser = MyInputParaser(input_data)
        item = to_new_put_item(parser)
        table.put_item(Item=item)
    """
    item = asdict(parser.input_data)
    assert isinstance(item, dict)
    item = {
        k: v.name if isinstance(v, Enum) else v for k, v in item.items()}
    item = dict_to_camel_case(item)
    item['PK'] = parser.get_pk()
    item['SK'] = parser.get_sk()
    __, pk_gsi1 = parser.get_pk_gsi1()
    item['PK_GSI1'] = pk_gsi1
    __, sk_gsi1 = parser.get_sk_gsi1()
    item['SK_GSI1'] = sk_gsi1
    return item


def to_update_item_kwargs(
        parser: AbstracInputParser) -> Dict[str, Any]:
    """
    Create the keyword arguments to pass to boto3 dynamodb `table.update_item()`

    DynamoDB data is mostly queried from GraphQL, so field names are converted
    to camel case for the sake of simplicity in resolvers.

    Usage::

        input_data = MyInput(field_1='a', field_2='b')
        paraser = MyInputParaser(input_data)
        update_kwargs = to_update_item_kwargs(parser)
        table.update_item(**update_kwargs)
    """
    result: Dict[str, Any] = {}
    result['Key'] = {'PK': parser.get_pk(), 'SK': parser.get_sk()}

    update_expression: List[str] = []
    expression_attribute_values: Dict[str, Any] = {}
    expression_attribute_names: Dict[str, Any] = {}

    for field in fields(parser.input_data):
        val = getattr(parser.input_data, field.name)
        if val is None:
            continue
        if field.name == 'id':
            expression_attribute_names['#id'] = 'id'
            continue
        elif val == '':
            val = None
        elif isinstance(val, Enum):
            val = val.name

        update_expression.append(f'#{field.name} = :{field.name}')
        expression_attribute_names[f'#{field.name}'] = to_camel_case(field.name)
        expression_attribute_values[f':{field.name}'] = val

    update_required, pk_gsi1 = parser.get_pk_gsi1()
    if update_required:
        update_expression.append('#PK_GSI1 = :PK_GSI1')
        expression_attribute_names['#PK_GSI1'] = 'PK_GSI1'
        expression_attribute_values[':PK_GSI1'] = pk_gsi1

    update_required, sk_gsi1 = parser.get_sk_gsi1()
    if update_required:
        update_expression.append('#SK_GSI1 = :SK_GSI1')
        expression_attribute_names['#SK_GSI1'] = 'SK_GSI1'
        expression_attribute_values[':SK_GSI1'] = sk_gsi1

    result['UpdateExpression'] = ''.join(
        ['SET ', ', '.join(update_expression)])
    result['ExpressionAttributeValues'] = expression_attribute_values
    result['ExpressionAttributeNames'] = expression_attribute_names
    result['ConditionExpression'] = 'attribute_exists(#id)'
    result['ReturnValues'] = 'ALL_NEW'
    return result


def graphql_payload_to_input(
        payload: Dict[str, Any],
        input_class=Type[AbstractInputData],
        **kwargs: str) -> AbstractInputData:
    """
    Instantiate an input data class from a dictionary payload.
    The payload is expected to be an argument from a graphql resolver event
    with camel case fields.
    Additional kwargs will be passed directly to the input data class on
    instantiation.
    """
    input_kwargs: Dict[str, Any] = kwargs or {}
    for field in fields(input_class):
        input_kwargs.setdefault(
            field.name,
            payload.get(to_camel_case(field.name), field.default))
    input_data: AbstractInputData = input_class(**input_kwargs)
    return input_data
