from datetime import datetime, timezone
import pytz
from typing import Any, Dict, List, Optional

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
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        event: Dict[str, Any] = {
            'notification_type': 'ADMIN_EMAIL',
            'template_name': template_name,
            'subject': subject,
        }

        if context:
            event['context'] = context

        self.publish_notification(event)

    def send_customer_notification(
        self,
        template_name: str,
        subject: str,
        recipients: List[str],
        context: Optional[Dict[str, Any]] = None,
        recipients_context: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        event: Dict[str, Any] = {
            'notification_type': 'CUSTOMER_EMAIL',
            'template_name': template_name,
            'subject': subject,
            'recipients': recipients,
        }

        if context:
            event['context'] = context

        if recipients_context:
            event['recipients_context'] = recipients_context

        self.publish_notification(event)


def to_notification_display_datetime(
    dt: datetime, tz_name: str = 'Europe/London'
) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=pytz.utc)

    tz = pytz.timezone(tz_name)
    dt_local = dt.astimezone(tz)
    return dt_local.strftime('%d %b %Y, %H:%M %p (%Z)')
