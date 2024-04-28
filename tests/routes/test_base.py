from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app


def test_positive_index(client: TestClient):
    resp = client.get(app.url_path_for("index"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"message": "Api do confiacim"}


def test_positive_health(client: TestClient):
    resp = client.get(app.url_path_for("health"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"status": "ok"}


def test_negative_health(mocker, client: TestClient):
    mocker.patch("confiacim_api.routes.base.check_db", return_value=False)

    resp = client.get(app.url_path_for("health"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"status": "fail"}
