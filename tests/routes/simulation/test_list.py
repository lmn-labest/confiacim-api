import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Simulation

ROUTE_LIST_NAME = "simulation_list"


@pytest.mark.integration
def test_positive_list_only_user_simulation(
    client: TestClient,
    simulation_list: list[Simulation],
    token: str,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert len(body["simulations"]) == 2

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert len(body["simulations"]) == 1


@pytest.mark.integration
def test_positive_check_fields(
    client: TestClient,
    simulation_list: list[Simulation],
    token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    simulations = resp.json()["simulations"]

    assert len(simulations) == 2

    fields = simulations[0].keys()

    exepected = {"id", "tag", "user"}

    for f in fields:
        assert f in exepected


@pytest.mark.integration
def test_positive_list_empty(client: TestClient, token: str):

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    simulations_list_from_api = body["simulations"]

    assert len(simulations_list_from_api) == 0


@pytest.mark.integration
def test_negative_list_must_have_token(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
