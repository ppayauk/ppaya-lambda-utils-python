import json
from typing import Any


def load_sns_message_from_sqs(msg: Any) -> Any:
    return json.loads(json.loads(json.loads(msg.body)['Message'])['default'])
