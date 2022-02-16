from __future__ import annotations
from decimal import Decimal
import io
import json
from typing import List, TYPE_CHECKING
from unittest.mock import Mock


from ppaya_lambda_utils.exceptions import InvokeLambdaFunctionException, WorkflowException
from ppaya_lambda_utils.testing_utils import load_sns_message_from_sqs

import pytest

from ppaya_lambda_utils.boto_utils import (
    invoke_lambda_function, send_to_sqs, boto_clients, publish_to_sns,
    start_sync_workflow)

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import SendMessageBatchRequestEntryTypeDef


def test_get_client(powertools_logger, sns) -> None:
    client_1 = boto_clients.get_client('sns')
    client_2 = boto_clients.get_client('sns')

    assert client_1 is client_2


def test_get_resource(powertools_logger, sqs_queue) -> None:
    resource_1 = boto_clients.get_resource('sqs')
    resource_2 = boto_clients.get_resource('sqs')

    assert resource_1 is resource_2


def test_send_to_sqs(sqs_queue) -> None:
    entries: List[SendMessageBatchRequestEntryTypeDef] = [
        {'Id': str(x), 'MessageBody': str(x)} for x in range(22)]
    sqs = boto_clients.get_resource('sqs')
    resp = send_to_sqs(sqs, sqs_queue.url, entries)

    assert len(resp) == 22

    for x in range(22):
        message = sqs_queue.receive_messages(MaxNumberOfMessages=1)[0]
        assert message.message_id in resp
        assert message.body == str(x)

    assert len(sqs_queue.receive_messages()) == 0


def test_publish_to_sns(sns_topic, sns_subscription) -> None:
    sns = boto_clients.get_client('sns')
    message_in = {'x': 'y', 'my_decimal': Decimal('2.6')}
    message_attributes = {
        'message_type': {'DataType': 'String', 'StringValue': 'test'}}
    publish_to_sns(sns, sns_topic.arn, message_in, message_attributes)

    message_out = sns_subscription.receive_messages(MaxNumberOfMessages=1)[0]
    assert load_sns_message_from_sqs(message_out) == {'x': 'y', 'my_decimal': '2.6'}


def test_publish_to_sns_without_attributes(sns_topic, sns_subscription) -> None:
    sns = boto_clients.get_client('sns')
    message = {'x': 'y'}
    publish_to_sns(sns, sns_topic.arn, message)

    message = sns_subscription.receive_messages(MaxNumberOfMessages=1)[0]
    assert message == message


def test_invoke_lambda_function_with_event_invocation_type(mocker):
    mock_lambda_client = Mock()
    mock_lambda_client().invoke.return_value = {'StatusCode': 202}
    mocker.patch.object(boto_clients, 'get_client', mock_lambda_client)

    invoke_lambda_function('test_func', {'msg': 'blah'})


def test_invoke_lambda_function_with_error(mocker):
    mock_lambda_client = Mock()
    mock_lambda_client().invoke.return_value = {'StatusCode': 400}
    mocker.patch.object(boto_clients, 'get_client', mock_lambda_client)

    with pytest.raises(InvokeLambdaFunctionException):
        invoke_lambda_function('test_func', {'msg': 'blah'})


def test_invoke_lambda_function_with_request_response_invocation_type(mocker):
    mock_lambda_client = Mock()
    mock_lambda_client().invoke.return_value = {
        'StatusCode': 200,
        'Payload': io.StringIO('{"x": 1}'),
    }
    mocker.patch.object(boto_clients, 'get_client', mock_lambda_client)

    resp = invoke_lambda_function('test_func', {'msg': 'blah'}, 'RequestResponse')

    assert resp == {'x': 1}


def test_start_sync_workflow(mocker):
    mock_sfn_client = Mock()
    output = {'b': 2}
    mock_sfn_client().start_sync_execution.return_value = {
        'status': 'SUCCEEDED',
        'output': json.dumps(output),
    }
    mocker.patch.object(boto_clients, 'get_client', mock_sfn_client)

    resp = start_sync_workflow({'a': 1}, 'state-machine-arn')

    assert resp == output


def test_start_sync_workflow_with_failure(mocker):
    mock_sfn_client = Mock()
    error_cause = {'errorMessage': 'Oops', 'errorType': 'OopsError'}
    mock_sfn_client().start_sync_execution.return_value = {
        'status': 'FAILED',
        'cause': json.dumps(error_cause),
    }
    mocker.patch.object(boto_clients, 'get_client', mock_sfn_client)

    with pytest.raises(WorkflowException) as err_info:
        start_sync_workflow({'a': 1}, 'state-machine-arn')
    assert str(err_info.value) == 'OopsError: Oops'
