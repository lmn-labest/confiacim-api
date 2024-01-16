from confiacim_api.app import app
from fastapi import status
from fastapi.testclient import TestClient

ROUTE_LIST_NAME = "simulation_list"
ROUTE_RETRIVE_NAME = "simulation_retrive"


def test_positive_list(client: TestClient, simulation_list):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    simulations_list_from_api = body["simulations"]

    assert len(simulations_list_from_api) == 3

    for s, e in zip(simulations_list_from_api, simulation_list):
        assert s["id"] == e.id
        assert s["tag"] == e.tag


def test_positive_list_empty(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    simulations_list_from_api = body["simulations"]

    assert len(simulations_list_from_api) == 0


def test_positive_retrive(client: TestClient, simulation):
    resp = client.get(app.url_path_for(ROUTE_RETRIVE_NAME, simulation_id=simulation.id))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == simulation.id
    assert body["tag"] == simulation.tag


def test_negative_retrive(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_RETRIVE_NAME, simulation_id=404))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Simulation not found"}
