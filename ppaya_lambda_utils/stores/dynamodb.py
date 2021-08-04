from __future__ import annotations
from typing import Any, Dict, Generator, Optional, TYPE_CHECKING

from boto3.dynamodb.types import TypeDeserializer

from ppaya_lambda_utils.boto_utils import boto_clients
from ppaya_lambda_utils.stores.exceptions import ItemNotFoundException


if TYPE_CHECKING:
    from boto3.dynamodb.table import BatchWriter
    from mypy_boto3_dynamodb import DynamoDBServiceResource
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBStore(object):
    """
    A base class for creating and interacting with a dynamodb table.

    To limit connection latency to the initial, cold start invocation
    sub-classes should be instantiated only once eg::

        from ppaya_lambda_utils import DynamoDBStore


        MyStore(DynamoDBStore):
            table_name = 'my-table-name'

            def my_customer_method(self):
                pass


        my_store = MyStore()

    """
    table_name: Optional[str] = None
    _table: Optional[Table] = None
    _dynamodb: Optional[DynamoDBServiceResource] = None

    @property
    def table(self) -> Table:
        assert isinstance(self.table_name, str)
        if not self._table:
            self._table = self.dynamodb.Table(self.table_name)
        return self._table

    @property
    def dynamodb(self) -> DynamoDBServiceResource:
        if not self._dynamodb:
            self._dynamodb = boto_clients.get_resource('dynamodb')
        assert self._dynamodb is not None
        return self._dynamodb

    def get_batch_writer(self) -> BatchWriter:
        return self.table.batch_writer()

    def get_item(self, pkey: str, skey: str) -> Any:
        item = self.table.get_item(Key={'PK': pkey, 'SK': skey})
        try:
            return item['Item']
        except KeyError:
            raise ItemNotFoundException(f'Item not found PK: {pkey}, SK: {skey}')

    def delete_item(self, pkey: str, skey: str, batch=None) -> Any:
        delete_kwargs: Dict[str, Any] = {
            'Key': {'PK': pkey, 'SK': skey},
        }
        if batch:
            batch.delete_item(**delete_kwargs)
        else:
            delete_kwargs['ReturnValues'] = 'ALL_OLD'
            response = self.table.delete_item(**delete_kwargs)
            return response.get('Attributes', {})


def from_dynamodb_to_json(item) -> Dict[str, Any]:
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(value=v) for k, v in item.items()}


def paginated_results(
    operation: str, paginate_config: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    """
    Yield items from a paginator for a given operation and config.

    Usage::

        paginate_config: Dict[str, Any] = {
            'TableName': quote_store.table_name,
            'Select': 'ALL_ATTRIBUTES',
        }
        for item in paginated_results('scan', paginate_config):
            # per item logic
    """
    client = boto_clients.get_client('dynamodb')
    paginator = client.get_paginator(operation)
    response_iterator = paginator.paginate(**paginate_config)
    for response in response_iterator:
        for item in response['Items']:
            yield from_dynamodb_to_json(item)
