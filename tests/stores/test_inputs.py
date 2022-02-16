from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Union

from ppaya_lambda_utils.stores.inputs import (
    AbstractInputData, AbstracInputParser,
    to_new_put_item, to_update_item_kwargs, graphql_payload_to_input)


class MyTestStatus(Enum):
    ACTIVE = 1
    DELETED = 2


@dataclass
class NestedDataClass(AbstractInputData):
    field_one: MyTestStatus
    field_two: int


@dataclass
class CreateTestInput(AbstractInputData):
    id: str
    name: str
    size: float
    nested_data: List[NestedDataClass]
    created_by: str
    created_at: datetime
    my_flag: bool = False
    company_number: Optional[str] = None
    company_type: Optional[str] = None
    item_type: str = 'TEST'
    status: MyTestStatus = MyTestStatus.ACTIVE


@dataclass
class UpdateTestInput(AbstractInputData):
    id: str
    updated_at: datetime
    name: Optional[str] = None
    size: Optional[float] = None
    my_flag: Optional[bool] = None
    nested_data: Optional[List[NestedDataClass]] = None
    company_number: Optional[str] = None
    company_type: Optional[str] = None
    status: Optional[MyTestStatus] = None


class MyTestInputParser(AbstracInputParser):
    def __init__(
            self,
            input_data: Union[CreateTestInput, UpdateTestInput]) -> None:
        self.input_data = input_data

    def get_pk(self) -> str:
        return f'TEST#{self.input_data.id}'

    def get_sk(self) -> str:
        return self.get_pk()

    def get_pk_gsi1(self) -> Tuple[bool, str]:
        return False, 'TEST'

    def get_sk_gsi1(self) -> Tuple[bool, str]:
        requires_update = self.input_data.name is not None
        if requires_update:
            key = f'COMPANY#{self.input_data.company_number}'
        else:
            key = ''
        return requires_update, key


def test_to_new_put_item() -> None:
    input_data = CreateTestInput(
        id='id-1',
        name='Test',
        size=1.5,
        nested_data=[NestedDataClass(field_one=MyTestStatus.ACTIVE, field_two=2)],
        created_by='123',
        company_number='CO1',
        company_type='PLC',
        created_at=datetime(2021, 4, 29, 23, 0, 0, tzinfo=timezone.utc)
    )
    parser = MyTestInputParser(input_data)

    expected = {
        'PK': 'TEST#id-1',
        'SK': 'TEST#id-1',
        'PK_GSI1': 'TEST',
        'SK_GSI1': 'COMPANY#CO1',
        'id': 'id-1',
        'name': 'Test',
        'size': Decimal('1.5'),
        'myFlag': False,
        'nestedData': [{'fieldOne': MyTestStatus.ACTIVE.name, 'fieldTwo': 2}],
        'createdBy': '123',
        'companyNumber': 'CO1',
        'companyType': 'PLC',
        'createdAt': '2021-04-29T23:00:00+00:00',
        'itemType': 'TEST',
        'status': MyTestStatus.ACTIVE.name,
    }
    item = to_new_put_item(parser)
    assert item == expected
    assert isinstance(item['size'], Decimal)


def test_to_update_item_args() -> None:
    record = UpdateTestInput(
        id='id-1',
        name='Test 2',
        size=2.5,
        my_flag=False,
        nested_data=[NestedDataClass(field_one=MyTestStatus.ACTIVE, field_two=2)],
        company_number='CO2',
        status=MyTestStatus.DELETED,
        updated_at=datetime(2021, 4, 20, 23, 0, 0)
    )
    parser = MyTestInputParser(record)

    expected = {
        'Key': {'PK': 'TEST#id-1', 'SK': 'TEST#id-1'},
        'UpdateExpression': (
            'SET #updated_at = :updated_at, '
            '#name = :name, '
            '#size = :size, '
            '#my_flag = :my_flag, '
            '#nested_data = :nested_data, '
            '#company_number = :company_number, '
            '#status = :status, '
            '#SK_GSI1 = :SK_GSI1'
        ),
        'ExpressionAttributeValues': {
            ':updated_at': '2021-04-20T23:00:00+00:00',
            ':name': 'Test 2',
            ':size': Decimal('2.5'),
            ':my_flag': False,
            ':nested_data': [{'fieldOne': MyTestStatus.ACTIVE.name, 'fieldTwo': 2}],
            ':company_number': 'CO2',
            ':status': 'DELETED',
            ':SK_GSI1': 'COMPANY#CO2',
        },
        'ExpressionAttributeNames': {
            '#id': 'id',
            '#updated_at': 'updatedAt',
            '#name': 'name',
            '#size': 'size',
            '#my_flag': 'myFlag',
            '#nested_data': 'nestedData',
            '#company_number': 'companyNumber',
            '#status': 'status',
            '#SK_GSI1': 'SK_GSI1',
        },
        'ConditionExpression': 'attribute_exists(#id)',
        'ReturnValues': 'ALL_NEW',
    }
    assert to_update_item_kwargs(parser) == expected


def test_graphql_payload_to_input() -> None:
    payload = {
        'id': 'test-2',
        'name': 'Test 1',
        'size': 1.5,
        'myFlag': False,
        'nestedData': [{'fieldOne': MyTestStatus.ACTIVE.name, 'fieldTwo': 2}],
        'companyNumber': 'CO2',
        'updatedAt': '2021-04-20T23:00:00Z',
    }

    assert isinstance(payload['nestedData'], list)
    nested_data = [
        graphql_payload_to_input(x, NestedDataClass)
        for x in payload['nestedData']]

    result = graphql_payload_to_input(
        payload,
        UpdateTestInput,
        nested_data=nested_data)

    assert isinstance(result, UpdateTestInput)
    assert result.id == 'test-2'
    assert result.name == 'Test 1'
    assert result.size == 1.5
    assert result.my_flag is False
    assert result.nested_data == [NestedDataClass(field_one=MyTestStatus.ACTIVE, field_two=2)]
    assert result.company_number == 'CO2'
    assert result.updated_at == datetime(
        2021, 4, 20, 23, 0, 0, tzinfo=timezone.utc)
    assert result.company_type is None


def test_graphql_payload_to_input_with_kwarg_overrides() -> None:
    payload = {
        'id': 'test-2',
        'name': 'Test 1',
        'size': 1.5,
        'companyNumber': 'CO2',
        'status': 'DELETED',
    }

    result = graphql_payload_to_input(
        payload,
        UpdateTestInput,
        updated_at='2021-04-20T23:00:00Z')

    assert isinstance(result, UpdateTestInput)
    assert result.id == 'test-2'
    assert result.name == 'Test 1'
    assert result.size == 1.5
    assert result.company_number == 'CO2'
    assert result.updated_at == '2021-04-20T23:00:00Z'
    assert result.company_type is None
    assert result.status == MyTestStatus.DELETED
