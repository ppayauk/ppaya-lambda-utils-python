from ppaya_lambda_utils.notification_utils import NotificationClient
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
