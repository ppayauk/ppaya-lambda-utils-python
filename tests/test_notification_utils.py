from datetime import datetime

import pytest

from ppaya_lambda_utils.notification_utils import (
    NotificationClient, to_notification_display_datetime)
from ppaya_lambda_utils.testing_utils import load_sns_message_from_sqs


def test_send_admin_notification(sns_topic, sns_subscription) -> None:
    client = NotificationClient(sns_topic.arn)
    client.send_admin_notification('my_template', 'My Subject', {'a': 1})

    messages = sns_subscription.receive_messages()
    assert len(messages) == 1
    message = messages[0]
    published_message = load_sns_message_from_sqs(message)
    assert published_message['event'] == {
        'notification_type': 'ADMIN_EMAIL',
        'template_name': 'my_template',
        'subject': 'My Subject',
        'context': {'a': 1},
    }


def test_send_customer_notification(sns_topic, sns_subscription) -> None:
    client = NotificationClient(sns_topic.arn)
    client.send_customer_notification(
        'my_template',
        'My Subject',
        ['paul@ppaya.co.uk'],
        {'a': 1},
        {'paul@ppaya.co.uk': {'b': 2}}
    )

    messages = sns_subscription.receive_messages()
    assert len(messages) == 1
    message = messages[0]
    published_message = load_sns_message_from_sqs(message)
    assert published_message['event'] == {
        'notification_type': 'CUSTOMER_EMAIL',
        'template_name': 'my_template',
        'subject': 'My Subject',
        'recipients': ['paul@ppaya.co.uk'],
        'context': {'a': 1},
        'recipients_context': {'paul@ppaya.co.uk': {'b': 2}},
    }


@pytest.mark.parametrize(
    'dt_iso, expected', [
        ('2021-10-29T12:45:00+01:00', '29 Oct 2021, 12:45 PM (BST)'),
        ('2021-10-29T12:45:00', '29 Oct 2021, 13:45 PM (BST)'),
        ('2022-11-29T12:45:00+00:00', '29 Nov 2022, 12:45 PM (GMT)'),
    ]
)
def test_to_notification_display_datetime(dt_iso, expected) -> None:
    dt = datetime.fromisoformat(dt_iso)
    assert to_notification_display_datetime(dt) == expected
