from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Union

from ppaya_lambda_utils.stores.inputs import (
    AbstractInputData, AbstracInputParser,
    to_new_put_item, to_update_item_kwargs, graphql_payload_to_input)


class TestStatus(Enum):
    ACTIVE = 1
    DELETED = 2


@dataclass
class CreateTestInput(AbstractInputData):
    id: str
    name: str
    created_by: str
    created_at: str
    company_number: Optional[str] = None
    company_type: Optional[str] = None
    item_type: str = 'TEST'
    status: TestStatus = TestStatus.ACTIVE


@dataclass
class UpdateTestInput(AbstractInputData):
    id: str
    updated_at: str
    name: Optional[str] = None
    company_number: Optional[str] = None
    company_type: Optional[str] = None
    status: Optional[TestStatus] = None


class TestInputParser(AbstracInputParser):
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
        created_by='123',
        company_number='CO1',
        company_type='PLC',
        created_at='2021-04-29T23:00:00Z'
    )
    parser = TestInputParser(input_data)

    expected = {
        'PK': 'TEST#id-1',
        'SK': 'TEST#id-1',
        'PK_GSI1': 'TEST',
        'SK_GSI1': 'COMPANY#CO1',
        'id': 'id-1',
        'name': 'Test',
        'createdBy': '123',
        'companyNumber': 'CO1',
        'companyType': 'PLC',
        'createdAt': '2021-04-29T23:00:00Z',
        'itemType': 'TEST',
        'status': TestStatus.ACTIVE.name,
    }
    assert to_new_put_item(parser) == expected


def test_to_update_item_args() -> None:
    record = UpdateTestInput(
        id='id-1',
        name='Test 2',
        company_number='CO2',
        updated_at='2021-04-20T23:00:00Z'
    )
    parser = TestInputParser(record)

    expected = {
        'Key': {'PK': 'TEST#id-1', 'SK': 'TEST#id-1'},
        'UpdateExpression': (
            'SET #updated_at = :updated_at, '
            '#name = :name, '
            '#company_number = :company_number, '
            '#SK_GSI1 = :SK_GSI1'
        ),
        'ExpressionAttributeValues': {
            ':updated_at': '2021-04-20T23:00:00Z',
            ':name': 'Test 2',
            ':company_number': 'CO2',
            ':SK_GSI1': 'COMPANY#CO2',
        },
        'ExpressionAttributeNames': {
            '#id': 'id',
            '#updated_at': 'updatedAt',
            '#name': 'name',
            '#company_number': 'companyNumber',
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
        'companyNumber': 'CO2',
    }

    result = graphql_payload_to_input(
        payload,
        UpdateTestInput,
        updated_at='2021-04-20T23:00:00Z')

    assert isinstance(result, UpdateTestInput)
    assert result.id == 'test-2'
    assert result.name == 'Test 1'
    assert result.company_number == 'CO2'
    assert result.updated_at == '2021-04-20T23:00:00Z'
    assert result.company_type is None
