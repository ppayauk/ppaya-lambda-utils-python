from __future__ import annotations
from typing import Any, Callable, Dict, TYPE_CHECKING

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext


if TYPE_CHECKING:
    from aws_lambda_powertools import Logger, Metrics


@lambda_handler_decorator
def observability_init_middleware(
        handler: Callable, event: Dict[str, Any], context: LambdaContext,
        logger: Logger, metrics: Metrics, log_structure: Dict[str, str] = None,
        *args, **kwargs) -> Any:
    """
    An aws_lambda_powertools middleware function setting up standard logging
    and metrics handling for lambda functions.
    """
    if log_structure:
        logger.structure_logs(append=True, **log_structure)
    metrics.add_metadata(key='handler_name', value=handler.__module__)
    try:
        result = handler(event, context)
    except Exception as err:
        metrics.add_metric(name='function_failed', unit='Count', value=1)
        logger.error(
            {'msg': 'Function failed', 'error': str(err), 'event': event})
        raise
    else:
        metrics.add_metric(name='function_succeeded', unit='Count', value=1)
    return result
