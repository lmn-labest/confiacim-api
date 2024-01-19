from confiacim_api.app import app
from confiacim_api.models import Simulation
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

ROUTE_LIST_NAME = "simulation_list"
ROUTE_RETRIVE_NAME = "simulation_retrive"
ROUTE_DELETE_NAME = "simulation_delete"
ROUTE_PATCH_NAME = "simulation_patch"
ROUTE_CREATE_NAME = "simulation_create"


def test_positive_list(client: TestClient, simulation_list: list[Simulation]):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    simulations_list_from_api = body["simulations"]

    assert len(simulations_list_from_api) == 3

    for s, e in zip(simulations_list_from_api, simulation_list):
        assert s["id"] == e.id
        assert s["tag"] == e.tag
        if e.celery_task_id:
            assert s["celery_task_id"] == str(e.celery_task_id)
        else:
            assert s["celery_task_id"] is None


def test_positive_list_empty(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    simulations_list_from_api = body["simulations"]

    assert len(simulations_list_from_api) == 0


def test_positive_retrive(client: TestClient, simulation: Simulation):
    resp = client.get(app.url_path_for(ROUTE_RETRIVE_NAME, simulation_id=simulation.id))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == simulation.id
    assert body["tag"] == simulation.tag


def test_negative_retrive_not_found(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_RETRIVE_NAME, simulation_id=404))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Simulation not found"}


def test_positive_delete(client: TestClient, simulation: Simulation, session):
    resp = client.delete(app.url_path_for(ROUTE_DELETE_NAME, simulation_id=simulation.id))

    assert resp.status_code == status.HTTP_204_NO_CONTENT

    assert not session.scalar(select(Simulation).where(Simulation.id == simulation.id))


def test_negative_delete_not_found(client: TestClient):
    resp = client.delete(app.url_path_for(ROUTE_DELETE_NAME, simulation_id=404))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Simulation not found"}


def test_positive_patch(client: TestClient, simulation: Simulation, session):
    payload = {"tag": "simulation_2"}

    resp = client.patch(
        app.url_path_for(ROUTE_PATCH_NAME, simulation_id=simulation.id),
        json=payload,
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    session.refresh(simulation)

    assert body == {"id": simulation.id, "tag": payload["tag"], "celery_task_id": None}

    assert simulation.tag == payload["tag"]


def test_negative_patch_not_found(client: TestClient):
    payload = {"tag": "simulation_2"}

    resp = client.patch(
        app.url_path_for(ROUTE_PATCH_NAME, simulation_id=404),
        json=payload,
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Simulation not found."}


def test_negative_patch_tag_name_should_be_unique(
    client: TestClient,
    simulation: Simulation,
    outher_simulation: Simulation,
):
    payload = {"tag": "simulation_1"}

    resp = client.patch(
        app.url_path_for(ROUTE_PATCH_NAME, simulation_id=outher_simulation.id),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = resp.json()

    assert body == {"detail": "Simulation Tag name shoud be unique."}


def test_positive_patch_update_to_same_tag_name(client: TestClient, simulation: Simulation, session):
    payload = {"tag": simulation.tag}

    resp = client.patch(
        app.url_path_for(ROUTE_PATCH_NAME, simulation_id=simulation.id),
        json=payload,
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    session.refresh(simulation)

    assert body == {"id": simulation.id, "tag": payload["tag"], "celery_task_id": None}

    assert simulation.tag == payload["tag"]


def test_positive_create(client: TestClient, session):
    payload = {"tag": "simulation_1"}

    resp = client.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_201_CREATED

    db_simulation = session.scalars(select(Simulation)).first()

    assert db_simulation.id
    assert db_simulation.tag == payload["tag"]

    body = resp.json()

    assert body["id"] == db_simulation.id
    assert body["tag"] == payload["tag"]


def test_negative_create_missing_tag(client: TestClient, session):
    payload = {"tag1": "1"}

    resp = client.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    db_simulation = session.scalars(select(Simulation)).first()

    assert not db_simulation

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "Field required"
    assert body["detail"][0]["type"] == "missing"


def test_negative_create_missing_tag_must_be_lt_30(client: TestClient, session):
    payload = {"tag": "s" * 31}

    resp = client.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    db_simulation = session.scalars(select(Simulation)).first()

    assert not db_simulation

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "String should have at most 30 characters"
    assert body["detail"][0]["type"] == "string_too_long"


def test_negative_create_tag_name_should_be_unique(
    client: TestClient,
    simulation: Simulation,
    outher_simulation: Simulation,
):
    payload = {"tag": "simulation_1"}

    resp = client.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "Simulation Tag name shoud be unique."}
