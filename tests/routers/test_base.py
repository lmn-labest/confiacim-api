import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api import __version__


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


@pytest.mark.integration
def test_system_stats(mocker, client: TestClient):

    mocker.patch("confiacim_api.routers.base.celery_app.control.inspect")
    mocker.patch("confiacim_api.routers.base.count_tasks", return_value=2)
    mocker.patch("confiacim_api.routers.base.total_success_simulations", return_value=3)
    mocker.patch("confiacim_api.routers.base.count_case_with_simulation_success", return_value=10)

    resp = client.get(app.url_path_for("system_stats"))

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {
        "number_of_simulations_in_queue": 2,
        "runnings_simulation": 2,
        "total_simulation": 3,
        "total_projects_with_simulations": 10,
    }


def test_versions(mocker, client: TestClient):

    mocker.patch("confiacim_api.routers.base.core_versions", return_value="Confiacim 0.16.0 (tencim1D 24.04.06)")

    resp = client.get(app.url_path_for("versions"))

    assert resp.json() == {
        "api": __version__,
        "core": "0.16.0",
        "tencim1D": "24.04.06",
    }
