import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app


@pytest.mark.integration
def test_positive_index(client: TestClient):
    resp = client.get(app.url_path_for("index"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"message": "Api do confiacim"}


@pytest.mark.integration
def test_positive_health(client: TestClient):
    resp = client.get(app.url_path_for("health"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"status": "ok"}


@pytest.mark.integration
def test_negative_health(mocker, client: TestClient):
    mocker.patch("confiacim_api.routers.base.check_db", return_value=False)

    resp = client.get(app.url_path_for("health"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"status": "fail"}
