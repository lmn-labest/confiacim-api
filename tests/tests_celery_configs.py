from confiacim_api.celery import get_config_transport


def test_get_config_transport():

    Settings = type("Settings", (), {"VISIBILITY_TIMEOUT": 86400, "SENTINEL_MASTER_NAME": None})

    settings = Settings()

    assert get_config_transport(settings) == {"visibility_timeout": 86400}


def test_get_config_transport_with_master_name():

    Settings = type("Settings", (), {"VISIBILITY_TIMEOUT": 86400, "SENTINEL_MASTER_NAME": "mymaster"})

    settings = Settings()

    assert get_config_transport(settings) == {
        "visibility_timeout": 86400,
        "master_name": "mymaster",
    }
