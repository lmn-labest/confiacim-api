import pytest

from confiacim_api.connection_string import postgresql_connection_url, sentinel_connection_url


@pytest.mark.unit
def test_connection_string_postgres():
    database_url = postgresql_connection_url(
        user="user",
        password="123456",
        host="host",
        db_name="db_name",
        port=5434,
    )

    assert database_url == "postgresql+psycopg://user:123456@host:5434/db_name"


@pytest.mark.unit
def test_connection_string_postgres_default_args():
    database_url = postgresql_connection_url(
        user="user",
        password="123456",
        host="host",
        db_name="db_name",
    )

    assert database_url == "postgresql+psycopg://user:123456@host:5432/db_name"


@pytest.mark.unit
def test_connection_string_sentinel():
    connection_url = sentinel_connection_url(host="host", password="123456", port=26380)

    assert connection_url == "sentinel://:123456@host:26380"


@pytest.mark.unit
def test_connection_string_sentinel_without_port():
    connection_url = sentinel_connection_url(host="host", password="123456")

    assert connection_url == "sentinel://:123456@host:26379"


@pytest.mark.unit
def test_connection_string_sentinel_without_password_and_port():
    connection_url = sentinel_connection_url(host="host")

    assert connection_url == "sentinel://host:26379"
