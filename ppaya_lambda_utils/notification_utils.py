from datetime import datetime, timezone
from typing import Any, Dict, List

from ppaya_lambda_utils.boto_utils import boto_clients, publish_to_sns


class NotificationClient(object):
    """
    Class encapsulating helper methods for publishing notifications to
    the internal PPAYA *notification_service*.

    Usage:

        client = NotificationClient(settings.NOTIFICATION_TOPIC)
        client.send_admin_notification(
            'my_template', 'My subject', {'data': 'blah'}
        )
    """
    def __init__(self, sns_topic: str) -> None:
        self.sns_topic = sns_topic

    def publish_notification(self, event: Dict[str, Any]) -> None:
        msg = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event': event,
        }
        msg_attr = {
            'event_type': {
                'DataType': 'String', 'StringValue': 'notify'
            }
        }
        sns = boto_clients.get_client('sns')
        publish_to_sns(sns, self.sns_topic, msg, msg_attr)

    def send_admin_notification(
        self,
        template_name: str,
        subject: str,
        context: Dict[str, Any]
    ) -> None:
        event = {
            'notification_type': 'ADMIN_EMAIL',
            'template_name': template_name,
            'subject': subject,
            'context': context,
        }

        self.publish_notification(event)

    def send_customer_notification(
        self,
        template_name: str,
        subject: str,
        context: Dict[str, Any],
        recipients: List[str]
    ) -> None:
        event = {
            'notification_type': 'CUSTOMER_EMAIL',
            'template_name': template_name,
            'subject': subject,
            'context': context,
            'recipients': recipients,
        }

        self.publish_notification(event)
