from ppaya_lambda_utils.api_utils import create_api_response


def test_create_api_response_ok() -> None:
    body = {'x': 'y'}
    assert create_api_response(body, 200) == {
            'statusCode': 200, 'body': '{"x": "y", "status": "OK"}'}


def test_create_api_response_fail() -> None:
    body = {'x': 'y'}
    assert create_api_response(body, 400) == {
            'statusCode': 400, 'body': '{"x": "y", "status": "FAIL"}'}
