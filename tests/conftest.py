import json

from aws_lambda_powertools import Logger
import boto3
from moto import (
    mock_ssm, mock_kms, mock_sns, mock_sqs, mock_dynamodb2)
import pytest


@pytest.fixture
def powertools_logger(scope='session'):
    return Logger()


@pytest.fixture(scope='module')
def kms():
    with mock_kms():
        yield boto3.client('kms')


@pytest.fixture(scope='module')
def kms_key(kms):
    yield kms.create_key()


@pytest.fixture(scope='module')
def ssm():
    with mock_ssm():
        yield boto3.client('ssm')


@pytest.fixture(scope='module')
def ssm_test(ssm, kms_key):
    secrets = {'SOME_PASSWORD': 'xxx-password-xxx'}
    ssm.put_parameter(
        Name='/my-app/secrets',
        Description='My app secrets',
        Value=json.dumps(secrets),
        Type='String',
        KeyId=kms_key['KeyMetadata']['KeyId'])


@pytest.fixture(scope='module')
def sns():
    with mock_sns():
        yield boto3.resource('sns')


@pytest.fixture(scope='function')
def sns_topic(sns):
    topic = sns.create_topic(Name='test-topic')
    yield topic


@pytest.fixture(scope='function')
def sqs():
    with mock_sqs():
        yield boto3.resource('sqs')


@pytest.fixture(scope='function')
def sns_subscription(sqs, sns_topic):
    queue = sqs.create_queue(QueueName="test-queue")
    sns_topic.subscribe(
        TopicArn=sns_topic.arn, Protocol='sqs',
        Endpoint=queue.attributes['QueueArn'])
    yield queue


@pytest.fixture(scope='function')
def sqs_queue(sqs):
    queue = sqs.create_queue(QueueName='test-queue')
    yield queue


@pytest.fixture(scope='function')
def dynamodb():
    with mock_dynamodb2():
        yield boto3.resource('dynamodb')


@pytest.fixture(scope='function')
def dynamodb_table(dynamodb):
    """Create a DynamoDB surveys table fixture."""
    table = dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {
                'AttributeName': 'PK',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'SK',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PK',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'SK',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        },
    )

    table.meta.client.get_waiter('table_exists').wait(
        TableName='test-table')
    yield table
