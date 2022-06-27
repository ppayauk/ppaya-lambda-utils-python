import json
from typing import Any, Dict


def load_sns_message_from_sqs(msg: Any) -> Any:
    return json.loads(json.loads(json.loads(msg.body)['Message'])['default'])


def create_sqs_event(message: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps({'Message': json.dumps(message)})
    return {
        'Records': [{
            'body': body,
        }],
    }
