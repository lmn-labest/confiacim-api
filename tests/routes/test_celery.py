# from uuid import uuid4

# import pytest
# from fastapi import status
# from fastapi.testclient import TestClient

# from confiacim_api.app import app
# from confiacim_api.models import Simulation

# ROUTE_RUN_SIMULATION = "simulation_run"


# @pytest.mark.integration
# def test_positive_run_simulation(mocker, client: TestClient, simulation: Simulation):
#     AsyncResultMock = type("AsyncResultMock", (), {"id": uuid4()})

#     run_task_delay = mocker.patch("confiacim_api.routes.celery.simulation_run_task.delay",
# return_value=AsyncResultMock)

#     resp = client.get(app.url_path_for(ROUTE_RUN_SIMULATION, simulation_id=simulation.id))

#     assert resp.status_code == status.HTTP_202_ACCEPTED

#     assert resp.json() == {
#         "message": f"A task
# '{AsyncResultMock.id}' da simulação '{simulation.tag}' foi mandada para a fila."  # type: ignore
#     }

#     run_task_delay.assert_called_once()
#     run_task_delay.assert_called_once_with(simulation_id=simulation.id)

#     assert simulation.celery_task_id == AsyncResultMock.id  # type: ignore


# @pytest.mark.integration
# def test_negative_run_simulation(client: TestClient):
#     resp = client.get(app.url_path_for(ROUTE_RUN_SIMULATION, simulation_id=404))

#     assert resp.status_code == status.HTTP_404_NOT_FOUND

#     assert resp.json() == {"detail": "Simulation not found."}
