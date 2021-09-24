from __future__ import annotations
import json
from typing import (
    Any, List, Literal, Optional, Set, Dict, TYPE_CHECKING, Union)

from aws_lambda_powertools.shared.json_encoder import Encoder
import boto3
from botocore.config import Config

from ppaya_lambda_utils.exceptions import InvokeLambdaFunctionException
from ppaya_lambda_utils.logging_utils import get_logger_factory

if TYPE_CHECKING:
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sqs import SQSServiceResource
    from mypy_boto3_sqs.type_defs import SendMessageBatchRequestEntryTypeDef
    from mypy_boto3_lambda.client import LambdaClient
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef


logger = get_logger_factory(__name__)()


class BotoClients(object):
    """
    Provides methods for creating boto3 clients and services and caches
    them internally, allowing them to be re-used across lambda invocations.
    This should limit connection latency to the initial, cold start invocation.

    Most of the time you will want to import the instantiated object from
    this module::

        # in your handler module.
        from botocore.config imoprt Config
        from ppaya_lambda_utils.boto_utils import boto_clients

        my_config = Config(retries={'max_attempts': 10, 'mode': 'standard'})
        boto_clients.set_default_config(my_config)

        def lambda_handler(event, context):
            s3 = boto_clients.get_client('s3')
    """
    # Internal cache to store boto resource objects and share between all
    # instances of the BotoResource class and across lambda invocations.
    _resources: Dict[str, Any] = {}
    _clients: Dict[str, Any] = {}
    _default_config: Optional[Config] = None

    def __init__(self, config: Optional[Config] = None) -> None:
        self.set_default_config(config)

    def set_default_config(self, config: Config) -> None:
        self._default_config = config

    def get_client(self, name: str, config: Optional[Config] = None) -> Any:
        config = config or self._default_config
        if name not in self._clients:
            logger.debug({'msg': 'Creating boto client', 'service': name})
            self._clients[name] = boto3.client(name, config=config)  # type: ignore
        return self._clients[name]

    def get_resource(self, name: str, config: Optional[Config] = None) -> Any:
        config = config or self._default_config
        if name not in self._resources:
            logger.debug({'msg': 'Creating boto resource', 'service': name})
            self._resources[name] = boto3.resource(name, config=config)  # type: ignore
        return self._resources[name]


boto_clients: BotoClients = BotoClients()


def publish_to_sns(
        client: SNSClient, topic_arn: str, message: Dict[str, Any],
        message_attributes: Optional[Dict[str, Any]] = None) -> None:
    """
    Publish a dictionary message to SNS as a JSON structure with optional
    message attribures which can be used for filtering by consumers.
    """
    logger.info(
        {'msg': 'Publishing to SNS', 'topic': topic_arn, 'body': message})
    message_attributes = message_attributes or {}
    client.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message, cls=Encoder)}),
        MessageStructure='json',
        MessageAttributes=message_attributes
    )


def send_to_sqs(
        resource: SQSServiceResource,
        queue_url: str,
        entries: List[SendMessageBatchRequestEntryTypeDef],
        max_batch_size: int = 10) -> Set[str]:
    """
    Send a list of dictionaries to an SQS queue.  A maximum of 10 messages
    can be sent in a single call to `send_messages` so if there are more than
    `max_batch_size` entries they will be sent in batches.
    """
    queue = resource.Queue(queue_url)
    message_ids = set()

    batches = [
        entries[x: x + max_batch_size]
        for x in range(0, len(entries), max_batch_size)]

    for batch in batches:
        result = queue.send_messages(Entries=batch)

        successful = result.get('Successful', [])
        failed = result.get('Failed', [])

        if failed:
            logger.error(
                {
                    'msg': (
                        f'Failed to publish {len(failed)} messages '
                        f'to {queue_url}'
                    ),
                    'failed': failed,
                }
            )

        message_ids.update([x['MessageId'] for x in successful])

    return message_ids


def invoke_lambda_function(
    function_name: str,
    payload: Dict[str, Any],
    invocation_type: Union[Literal['Event'], Literal['RequestResponse']] = 'Event'
) -> Any:
    client: LambdaClient = boto_clients.get_client('lambda')
    resp: InvocationResponseTypeDef = client.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=bytes(json.dumps(payload, cls=Encoder), encoding='utf-8')
    )

    success_codes: Dict[Union[Literal['Event'], Literal['RequestResponse']], int] = {
        'Event': 202, 'RequestResponse': 200}

    resp_payload_stream = resp.get('Payload')
    if resp_payload_stream:
        resp_payload = resp_payload_stream.read()
    else:
        resp_payload = b''

    if resp['StatusCode'] != success_codes[invocation_type] or resp.get('FunctionError'):
        logger.error({
            'msg': 'Invoke lambda function failed',
            'function_name': function_name,
            'response': resp,
            'response_payload': resp_payload,
            'payload': payload,
        })
        raise InvokeLambdaFunctionException(f'Invoke function failed: {function_name}')

    if invocation_type == 'RequestResponse':
        return json.loads(resp_payload)
