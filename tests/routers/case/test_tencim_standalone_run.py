from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case, User

ROUTE_NAME = "tencim_standalone_run"


@pytest.mark.integration
def test_positive_run(
    client_auth: TestClient,
    session,
    mocker,
    user: User,
    case_with_file: Case,
):
    task = MagicMock()
    task.id = str(uuid4())

    tencim_standalone_run_mocker = mocker.patch(
        "confiacim_api.routers.case.tencim_run.apply_async",
        return_value=task,
    )

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id))

    assert resp.status_code == status.HTTP_200_OK

    tencim_standalone_run_mocker.assert_called_once()
    tencim_standalone_run_mocker.assert_called_with(args=(1,))

    body = resp.json()

    assert body["detail"] == "Simulation sent to queue."
    assert body["task_id"] == task.id


@pytest.mark.integration
def test_negative_not_found(client_auth: TestClient):

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=404))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_if_case_not_have_base_file_return_400(
    client_auth: TestClient,
    case: Case,
):
    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "The case has no base file."}


@pytest.mark.integration
def test_negative_need_have_token(client: TestClient):

    resp = client.post(app.url_path_for(ROUTE_NAME, case_id=1))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"


@pytest.mark.integration
def test_negative_user_can_only_run_owns_cases(
    client: TestClient,
    case_with_file: Case,
    other_user_token: str,
):

    resp = client.post(
        app.url_path_for(ROUTE_NAME, case_id=case_with_file.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}