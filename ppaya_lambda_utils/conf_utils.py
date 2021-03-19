from datetime import datetime
import os
from typing import List, Optional

from aws_lambda_powertools.utilities import parameters
from botocore.config import Config


BOTO_CONFIG = Config(
    retries={
        'max_attempts': 10,
        'mode': 'standard',
    }
)


class BaseSettings(object):
    """
    A Settings class that adds functionality to retrieve values from environment
    variables and secrets from AWS SSM (Simple Systems Manager)
    parameter store.  Secrets can be cached for SECRETS_MAX_AGE seconds.

    The parameter is expected to be an encrypted, JSON string.

    Secrets must be explicitly loaded::

        settings.load_settings()

    This allows lazy loading the secrets at runtime and makes it easier to mock
    during unit tests.

    This is a poor mans implementation of the pydantic BaseSettings class,
    which unfortunately is too large a library to be included in a lambda
    function alongside other large libraries eg pandas.

    Usage::

        class MySettings(BaseSettings):
            SECRETS_KEY = '/my-app/secrets'

            ENV_NAME: str = 'dev'
            TABLE_NAME: str = 'default-table-name'
            SOME_PASSWORD: str = 'TBA'

            environ_fields: List[str] = [
                'ENV_NAME',
                'TABLE_NAME',
            ]

            secret_fields: List[str] = [
                'SOME_PASSWORD'
            ]
    """
    # Used internally for deterimining loading and caching behaviour.
    SECRETS_LOADED_AT: Optional[float] = None
    # Number of seconds secrets should be cached for.
    SECRETS_MAX_AGE: int = 30 * 60
    # The key / path of the SSM Parameter containing the secrets.
    # This should be defined in sub-classes.
    SECRETS_KEY: str = '/path/to/secrets'

    environ_fields: List[str] = []
    secret_fields: List[str] = []

    def __init__(self) -> None:
        self.load_environ_settings()
        self.USE_POWERTOOLS_LOGGING = (
            'POWERTOOLS_METRICS_NAMESPACE' in os.environ)

    def load_environ_settings(self) -> None:
        for name in self.environ_fields:
            value = os.environ.get(name, None)
            if value:
                cast_to = type(getattr(self, name))
                setattr(self, name, cast_to(value))

    def load_secret_settings(self) -> None:
        if self._is_secret_load_required():
            secrets = parameters.get_parameter(
                self.SECRETS_KEY, decrypt=True, transform='json')

            if isinstance(secrets, dict):
                for name in self.secret_fields:
                    value = secrets.get(name)
                    if value:
                        cast_to = type(getattr(self, name))
                        setattr(self, name, cast_to(value))

            self.SECRETS_LOADED_AT = datetime.utcnow().timestamp()

    def _is_secret_load_required(self) -> bool:
        if self.SECRETS_LOADED_AT:
            expires_at = self.SECRETS_LOADED_AT + self.SECRETS_MAX_AGE
            return datetime.utcnow().timestamp() > expires_at
        else:
            return True
