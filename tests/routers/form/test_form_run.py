from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from confiacim_api.app import app
from confiacim_api.models import Case, FormResult

ROUTE_NAME = "form_run"


@pytest.fixture
def payload():
    return {
        "variables": [
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
            {
                "name": "poisson_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
        ],
    }


@pytest.mark.integration
def test_positive_form_run(
    client_auth: TestClient,
    session,
    mocker,
    case_with_file: Case,
    payload,
):

    task = MagicMock()
    task.id = str(uuid4())

    form_run_mocker = mocker.patch(
        "confiacim_api.routers.form.form_task.delay",
        return_value=task,
    )

    url = app.url_path_for(ROUTE_NAME, case_id=case_with_file.id)

    resp = client_auth.post(url, json=payload)
    assert resp.status_code == status.HTTP_200_OK

    form_run_mocker.assert_called_once()
    form_run_mocker.assert_called_with(result_id=1)

    body = resp.json()

    result = session.scalars(select(FormResult)).one()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id


@pytest.mark.integration
@pytest.mark.parametrize(
    "variable, msg, type, loc",
    [
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": "not_number",
                    },
                },
            },
            "Input should be a valid number, unable to parse string as a number",
            "float_parsing",
            ["body", "variables", 0, "dist", "params", "mean"],
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "params": {
                        "mean": "not_number",
                    },
                },
            },
            "Field required",
            "missing",
            ["body", "variables", 0, "dist", "name"],
        ),
        (
            {
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": "not_number",
                    },
                },
            },
            "Field required",
            "missing",
            ["body", "variables", 0, "name"],
        ),
    ],
    ids=["mean_not_number", "dist_name_missing", "q"],
)
def test_negative_form_run_invalid_variables_params(
    client_auth: TestClient,
    case_with_file: Case,
    variable: dict,
    msg: str,
    type: str,
    loc: list,
):
    task = MagicMock()
    task.id = str(uuid4())

    payload = {"variables": [variable]}

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == loc
    assert detail["msg"] == msg
    assert detail["type"] == type


@pytest.mark.integration
def test_negative_form_run_must_have_at_least_one_variable(
    client_auth: TestClient,
    case_with_file: Case,
):
    task = MagicMock()
    task.id = str(uuid4())

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json={"variables": []})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == ["body", "variables"]
    assert detail["msg"] == "List should have at least 1 item after validation, not 0"
    assert detail["type"] == "too_short"


@pytest.mark.integration
def test_negative_not_found(client_auth: TestClient, payload):

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=404), json=payload)

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_if_case_not_have_base_file_return_400(
    client_auth: TestClient,
    case: Case,
    payload,
):
    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "The case has no base file."}


@pytest.mark.integration
def test_negative_need_have_token(client: TestClient, payload):

    resp = client.post(app.url_path_for(ROUTE_NAME, case_id=1), json=payload)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"


@pytest.mark.integration
def test_negative_user_can_only_run_owns_cases(
    client: TestClient,
    case_with_file: Case,
    other_user_token: str,
    payload,
):

    resp = client.post(
        app.url_path_for(ROUTE_NAME, case_id=case_with_file.id),
        json=payload,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}
