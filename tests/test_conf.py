import os

import pytest

from confiacim_api.conf import Settings


@pytest.fixture(scope="module", autouse=True)
def env():
    os.environ["CONFIACIM_API_DB_USER"] = "user"
    os.environ["CONFIACIM_API_DB_PASSWORD"] = "password"
    os.environ["CONFIACIM_API_DB_HOST"] = "localhost"
    os.environ["CONFIACIM_API_DB_NAME"] = "confiacim_api"
    os.environ["CONFIACIM_API_SENTINEL_HOST"] = "localhost"
    os.environ["CONFIACIM_API_JWT_SECRET_KEY"] = "Chave Secreta JWT"


@pytest.mark.unit
def test_configs_settings():

    settings = Settings(_env_file=None)

    assert settings.model_config["env_file"] == ".env"
    assert settings.model_config["env_file_encoding"] == "utf-8"
    assert settings.model_config["env_prefix"] == "confiacim_api_"


@pytest.mark.unit
def test_configs_default():

    settings = Settings(_env_file=None)

    assert settings.DB_PORT == 5432
    assert settings.SENTINEL_PORT == 26379
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert settings.VISIBILITY_TIMEOUT == 86400
