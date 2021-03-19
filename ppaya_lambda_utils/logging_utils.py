from __future__ import annotations
from functools import partial
import os
import logging
from typing import Union, Callable

from aws_lambda_powertools import Logger


def get_logger_factory(
        logger_name: str) -> Callable[[], Union[logging.Logger, Logger]]:
    """
    Returns a factory function to create a logger.  The returned function will
    create an aws_lambda_powertools child logger if supported.  Otherwise, a
    standard python logger is created.

    The powertools child logger needs to be instantiated in the module in which
    it will be used as it uses the caller frame at the point of instantiation.
    Consequently, we return a factory function to create the logger, no the
    logger itself.

    Usage::

        from ppaya_lambda_utils.logging_utils import get_logger_factory

        logger = get_logger_factory(__name__)()
    """
    if is_lambda_powertools_environment():
        return lambda: Logger(child=True)
    else:
        return partial(logging.getLogger, logger_name)


def is_lambda_powertools_environment() -> bool:
    """
    Use the 'POWERTOOLS_SERVICE_NAME' environment variable to deduce if
    aws_lambda_powertools logging is supported.
    """
    return 'POWERTOOLS_SERVICE_NAME' in os.environ
