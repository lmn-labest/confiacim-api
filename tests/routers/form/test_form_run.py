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
        "critical_point": 120,
        "form": {
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
        },
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

    result = session.scalars(select(FormResult)).one()

    form_run_mocker.assert_called_once()
    form_run_mocker.assert_called_with(result_id=result.id)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id

    assert result.config == payload["form"]
    assert result.critical_point == 120


@pytest.mark.integration
def test_positive_form_run_with_description(
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

    payload_new = payload.copy()
    payload_new["description"] = "Descricao do resultado."

    resp = client_auth.post(url, json=payload_new)

    assert resp.status_code == status.HTTP_200_OK

    result = session.scalars(select(FormResult)).one()

    form_run_mocker.assert_called_once()
    form_run_mocker.assert_called_with(result_id=result.id)

    body = resp.json()

    assert body["result_id"] == result.id
    assert body["task_id"] == task.id

    assert result.config == payload["form"]
    assert result.critical_point == 120
    assert result.description == "Descricao do resultado."


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
            ["body", "form", "variables", 0, "dist", "params", "mean"],
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
            ["body", "form", "variables", 0, "dist", "name"],
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
            ["body", "form", "variables", 0, "name"],
        ),
        (
            {
                "name": "E_i",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": "not_number",
                    },
                },
            },
            (
                "Input should be "
                "'E_c', 'poisson_c', 'thermal_expansion_c', "
                "'thermal_conductivity_c', 'volumetric_heat_capacity_c', 'friction_angle_c', "
                "'cohesion_c', 'E_f', 'poisson_f', 'thermal_expansion_f', "
                "'thermal_conductivity_f', 'volumetric_heat_capacity_f', "
                "'internal_pressure', 'internal_temperature' or 'external_temperature'"
            ),
            "enum",
            ["body", "form", "variables", 0, "name"],
        ),
    ],
    ids=[
        "mean_not_number",
        "dist_name_missing",
        "variable_name_missing",
        "invalid_variable_name",
    ],
)
def test_negative_form_run_invalid_variables(
    client_auth: TestClient,
    case_with_file: Case,
    variable: dict,
    msg: str,
    type: str,
    loc: list,
):

    payload = {
        "form": {"variables": [variable]},
        "critical_point": 120,
    }

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == loc
    assert detail["msg"] == msg
    assert detail["type"] == type


@pytest.mark.integration
@pytest.mark.parametrize(
    "payload, msg, type, loc",
    [
        (
            {
                "critical_point": -1,
                "form": {
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
                    ],
                },
            },
            "Input should be greater than 0",
            "greater_than",
            ["body", "critical_point"],
        ),
        (
            {
                "critical_point": "not_number",
                "form": {
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
                    ],
                },
            },
            "Input should be a valid integer, unable to parse string as an integer",
            "int_parsing",
            ["body", "critical_point"],
        ),
        (
            {
                "form": {
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
                    ],
                },
            },
            "Field required",
            "missing",
            ["body", "critical_point"],
        ),
    ],
    ids=["negative_critical_point", "critical_point_not_a_number", "critiacal_point_missing"],
)
def test_negative_form_run_invalid_critical_point(
    client_auth: TestClient,
    case_with_file: Case,
    payload: dict,
    msg: str,
    type: str,
    loc: list,
):

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == loc
    assert detail["msg"] == msg
    assert detail["type"] == type


def test_negative_form_run_invalid_distribution_name(
    client_auth: TestClient,
    case_with_file: Case,
    payload: dict,
):
    payload_new = payload.copy()
    payload_new["form"]["variables"][0]["dist"]["name"] = "invalid_name"

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == ["body", "form", "variables", 0, "dist", "name"]
    assert detail["msg"] == (
        "Input should be 'normal', 'lognormal', 'gumbel_r', "
        "'weibull_min', 'triang', 'sgld', 'sgld_lower_t' or 'sgld_lower_upper_t'"
    )
    assert detail["type"] == "enum"


@pytest.mark.integration
def test_negative_form_run_must_have_at_least_one_variable(
    client_auth: TestClient,
    case_with_file: Case,
):
    task = MagicMock()
    task.id = str(uuid4())

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case_with_file.id), json={"form": {"variables": []}})

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == ["body", "form", "variables"]
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
