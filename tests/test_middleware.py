from unittest.mock import Mock

from aws_lambda_powertools import Logger, Metrics
import pytest

from ppaya_lambda_utils.middleware import observability_init_middleware


logger = Logger()
metrics = Metrics()
log_structure = {'app_version': '0.0.1'}


@pytest.fixture
def lambda_event():
    return {'records': []}


@metrics.log_metrics
@logger.inject_lambda_context
@observability_init_middleware(
    logger=logger, metrics=metrics, log_structure=log_structure)
def my_handler_ok(event, context):
    metrics.add_metric(name='my_handler_ok', unit='Count', value=1)
    return {'result': 'OK'}


@metrics.log_metrics
@logger.inject_lambda_context
@observability_init_middleware(
    logger=logger, metrics=metrics, log_structure=log_structure)
def my_handler_fail(event, context):
    raise ValueError('Ooops')


def test_observability_init_middleware_ok(lambda_event) -> None:
    result = my_handler_ok(lambda_event, Mock())

    assert result == {'result': 'OK'}


def test_observability_init_middleware_fail(lambda_event) -> None:
    with pytest.raises(ValueError):
        my_handler_fail(lambda_event, Mock())
