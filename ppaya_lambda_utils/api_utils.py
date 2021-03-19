import json
from typing import Any, Dict


def create_api_response(
        body: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    A simple helper for consistent JSON responses to API Gateway events.
    """
    if status_code >= 300:
        body['status'] = 'FAIL'
    else:
        body['status'] = 'OK'

    return {
        'statusCode': status_code,
        'body': json.dumps(body),
    }
