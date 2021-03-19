from datetime import datetime
from typing import List

from freezegun import freeze_time

from ppaya_lambda_utils.conf_utils import BaseSettings


class MySettings(BaseSettings):
    SECRETS_KEY: str = '/my-app/secrets'

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


settings = MySettings()


def test_environment_variables() -> None:
    assert settings.ENV_NAME == 'local'
    assert settings.TABLE_NAME == 'test_table'


def test_environment_secrets(ssm_test) -> None:
    with freeze_time('2021-03-17 04:45:30'):
        settings.load_secret_settings()

        assert settings.SOME_PASSWORD == 'xxx-password-xxx'
        assert settings.SECRETS_LOADED_AT == datetime.now().timestamp()
        assert settings._is_secret_load_required() is False

    with freeze_time('2021-03-17 05:25:30'):
        assert settings._is_secret_load_required() is True
