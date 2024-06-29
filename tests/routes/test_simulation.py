# import pytest
# from fastapi import status
# from fastapi.testclient import TestClient
# from sqlalchemy import select

# from confiacim_api.app import app
# from confiacim_api.models import Simulation

# ROUTE_DELETE_NAME = "simulation_delete"
# ROUTE_PATCH_NAME = "simulation_patch"


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_positive_delete(client: TestClient, simulation: Simulation, session):
#     resp = client.delete(app.url_path_for(ROUTE_DELETE_NAME, simulation_id=simulation.id))

#     assert resp.status_code == status.HTTP_204_NO_CONTENT

#     assert not session.scalar(select(Simulation).where(Simulation.id == simulation.id))


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_negative_delete_not_found(client: TestClient):
#     resp = client.delete(app.url_path_for(ROUTE_DELETE_NAME, simulation_id=404))

#     assert resp.status_code == status.HTTP_404_NOT_FOUND

#     body = resp.json()

#     assert body == {"detail": "Simulation not found"}


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_positive_patch(client: TestClient, simulation: Simulation, session):
#     payload = {"tag": "simulation_2"}

#     resp = client.patch(
#         app.url_path_for(ROUTE_PATCH_NAME, simulation_id=simulation.id),
#         json=payload,
#     )

#     assert resp.status_code == status.HTTP_200_OK

#     body = resp.json()

#     session.refresh(simulation)

#     assert body == {"id": simulation.id, "tag": payload["tag"], "celery_task_id": None}

#     assert simulation.tag == payload["tag"]


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_negative_patch_not_found(client: TestClient):
#     payload = {"tag": "simulation_2"}

#     resp = client.patch(
#         app.url_path_for(ROUTE_PATCH_NAME, simulation_id=404),
#         json=payload,
#     )

#     assert resp.status_code == status.HTTP_404_NOT_FOUND

#     body = resp.json()

#     assert body == {"detail": "Simulation not found."}


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_negative_patch_tag_name_should_be_unique(
#     client: TestClient,
#     simulation: Simulation,
#     outher_simulation: Simulation,
# ):
#     payload = {"tag": "simulation_1"}

#     resp = client.patch(
#         app.url_path_for(ROUTE_PATCH_NAME, simulation_id=outher_simulation.id),
#         json=payload,
#     )

#     assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     body = resp.json()

#     assert body == {"detail": "Simulation Tag name shoud be unique."}


# @pytest.mark.skip(reason="Agora a simulação tem um relacionamento com usuario")
# @pytest.mark.integration
# def test_positive_patch_update_to_same_tag_name(client: TestClient, simulation: Simulation, session):
#     payload = {"tag": simulation.tag}

#     resp = client.patch(
#         app.url_path_for(ROUTE_PATCH_NAME, simulation_id=simulation.id),
#         json=payload,
#     )

#     assert resp.status_code == status.HTTP_200_OK

#     body = resp.json()

#     session.refresh(simulation)

#     assert body == {"id": simulation.id, "tag": payload["tag"], "celery_task_id": None}

#     assert simulation.tag == payload["tag"]
