from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from ppaya_lambda_utils.boto_utils import boto_clients


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
