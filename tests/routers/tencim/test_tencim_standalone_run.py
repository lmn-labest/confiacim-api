from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from confiacim_api.app import app
from confiacim_api.models import Case, TencimResult, User

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
        "confiacim_api.routers.tencim.tencim_run.delay",
        return_value=task,
    )

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json={})

    assert resp.status_code == status.HTTP_200_OK

    result = session.scalars(select(TencimResult)).one()

    tencim_standalone_run_mocker.assert_called_once()
    tencim_standalone_run_mocker.assert_called_with(result_id=result.id)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id


@pytest.mark.integration
@pytest.mark.parametrize(
    "value, boolean",
    [
        ("True", True),
        ("true", True),
        ("T", True),
        ("t", True),
        (1, True),
        ("False", False),
        ("false", False),
        ("F", False),
        ("f", False),
        (0, False),
    ],
)
def test_positive_run_with_rc_limit(
    client_auth: TestClient,
    session,
    mocker,
    user: User,
    case_with_file: Case,
    value,
    boolean,
):
    task = MagicMock()
    task.id = str(uuid4())

    tencim_standalone_run_mocker = mocker.patch(
        "confiacim_api.routers.tencim.tencim_run.delay",
        return_value=task,
    )

    payload = {"rc_limit": value}

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_200_OK

    result = session.scalars(select(TencimResult)).one()

    tencim_standalone_run_mocker.assert_called_once()
    tencim_standalone_run_mocker.assert_called_with(result_id=result.id, rc_limit=boolean)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id


@pytest.mark.integration
def test_positive_run_with_critical_point(
    client_auth: TestClient,
    session,
    mocker,
    user: User,
    case_with_file: Case,
):
    task = MagicMock()
    task.id = str(uuid4())

    tencim_standalone_run_mocker = mocker.patch(
        "confiacim_api.routers.tencim.tencim_run.delay",
        return_value=task,
    )

    payload = {"critical_point": 100}

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_200_OK

    result = session.scalars(select(TencimResult)).one()

    tencim_standalone_run_mocker.assert_called_once()
    tencim_standalone_run_mocker.assert_called_with(result_id=result.id, critical_point=100)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id

    assert result.critical_point == 100


@pytest.mark.integration
def test_positive_run_with_description(
    client_auth: TestClient,
    session,
    mocker,
    user: User,
    case_with_file: Case,
):
    task = MagicMock()
    task.id = str(uuid4())

    tencim_standalone_run_mocker = mocker.patch(
        "confiacim_api.routers.tencim.tencim_run.delay",
        return_value=task,
    )

    payload = {"description": "Descrição do resultado tencim"}

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_200_OK

    result = session.scalars(select(TencimResult)).one()

    tencim_standalone_run_mocker.assert_called_once()
    tencim_standalone_run_mocker.assert_called_with(result_id=result.id)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id

    assert result.description == "Descrição do resultado tencim"


@pytest.mark.integration
@pytest.mark.parametrize(
    "key, value, msg, type",
    [
        (
            "rc_limit",
            "dd",
            "Input should be a valid boolean, unable to interpret input",
            "bool_parsing",
        ),
        (
            "critical_point",
            "dd",
            "Input should be a valid integer, unable to parse string as an integer",
            "int_parsing",
        ),
        (
            "critical_point",
            "-1",
            "Input should be greater than 0",
            "greater_than",
        ),
        (
            "critical_point",
            "0",
            "Input should be greater than 0",
            "greater_than",
        ),
    ],
    ids=[
        "rc limit invalid type",
        "critical_point invalid type",
        "critical_point invalid value -1",
        "critical_point invalid value 0",
    ],
)
def test_negative_run_invalid_payload(
    client_auth: TestClient,
    case_with_file: Case,
    key: str,
    value: str,
    msg: str,
    type: str,
):
    task = MagicMock()
    task.id = str(uuid4())

    payload = {key: value}

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {
        "detail": [
            {
                "input": value,
                "loc": ["body", key],
                "msg": msg,
                "type": type,
            }
        ]
    }


@pytest.mark.integration
def test_negative_not_found(client_auth: TestClient):

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=404), json={})

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_if_case_not_have_base_file_return_400(
    client_auth: TestClient,
    case: Case,
):
    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json={})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "The case has no base file."}


@pytest.mark.integration
def test_negative_need_have_token(client: TestClient):

    resp = client.post(app.url_path_for(ROUTE_NAME, case_id=1), json={})

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
        json={},
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}
