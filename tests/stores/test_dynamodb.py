from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

import pytest

from ppaya_lambda_utils.stores.dynamodb import DynamoDBStore, paginated_results
from ppaya_lambda_utils.stores.exceptions import ItemNotFoundException


if TYPE_CHECKING:
    from boto3.dynamodb.table import BatchWriter


class MyTestStore(DynamoDBStore):
    table_name = 'test-table'

    def put_item(
            self,
            item: Dict['str', Any],
            batch: Optional[BatchWriter] = None) -> Any:

        if batch:
            batch.put_item(Item=item)
        else:
            self.table.put_item(Item=item)

        return item


my_test_store = MyTestStore()


def test_get_item(dynamodb_table) -> None:
    item = {'PK': '1', 'SK': '1', 'other': '3'}
    my_test_store.put_item(item)

    assert my_test_store.get_item('1', '1') == item


def test_delete_item(dynamodb_table) -> None:
    item = {'PK': '1', 'SK': '1', 'other': '3'}
    my_test_store.put_item(item)

    my_test_store.delete_item('1', '1')

    with pytest.raises(ItemNotFoundException):
        my_test_store.get_item('1', '1')


def test_batch_writer(dynamodb_table) -> None:
    item_1 = {'PK': '1', 'SK': '1', 'other': '1'}
    item_2 = {'PK': '2', 'SK': '2', 'other': '2'}
    item_3 = {'PK': '3', 'SK': '3', 'other': '3'}

    with my_test_store.get_batch_writer() as batch:
        my_test_store.put_item(item_1, batch)
        my_test_store.put_item(item_2, batch)
        my_test_store.put_item(item_3, batch)

    assert my_test_store.get_item('1', '1') == item_1
    assert my_test_store.get_item('2', '2') == item_2
    assert my_test_store.get_item('3', '3') == item_3


def test_paginated_results(dynamodb_table) -> None:
    expected_count = 2000
    with my_test_store.get_batch_writer() as batch:
        for i in range(expected_count):
            item = {'PK': 'X', 'SK': str(i)}
            my_test_store.put_item(item, batch)

    fetch_count = 0
    paginate_config: Dict[str, Any] = {
        'TableName': my_test_store.table_name,
        'Select': 'ALL_ATTRIBUTES',
    }
    for idx, item in enumerate(paginated_results('scan', paginate_config)):
        assert item['PK'] == 'X'
        assert item['SK'] == str(idx)
        fetch_count += 1

    assert fetch_count == expected_count
