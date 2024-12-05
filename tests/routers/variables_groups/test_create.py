import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from confiacim_api.app import app
from confiacim_api.database import Session
from confiacim_api.models import Case, User, VariableGroup

ROUTE_NAME = "variable_group_create"


@pytest.fixture()
def payload(variables_form: list, correlations_form: dict):
    return {
        "tag": "case_1",
        "description": "Qualquer descrição",
        "variables": variables_form,
        "correlations": correlations_form,
    }


@pytest.mark.integration
def test_positive_create(client_auth: TestClient, session, payload, case: Case):

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=payload)

    assert resp.status_code == status.HTTP_201_CREATED

    from_db = session.scalars(select(VariableGroup)).first()

    assert from_db.id
    assert from_db.tag == payload["tag"]
    assert from_db.case.id == case.id
    assert from_db.description == payload["description"]
    assert from_db.variables == payload["variables"]
    assert from_db.correlations == payload["correlations"]

    body = resp.json()

    assert body["id"] == from_db.id
    assert body["tag"] == from_db.tag
    assert body["case"] == from_db.case.id
    assert body["description"] == from_db.description

    assert body["variables"] == from_db.variables
    assert body["correlations"] == from_db.correlations

    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.integration
@pytest.mark.parametrize("field", ["description", "correlations"])
def test_positive_optional_payload_field(client_auth, case: Case, field: str, payload: dict):

    new_payload = payload.copy()
    del new_payload[field]

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=new_payload)

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.integration
@pytest.mark.parametrize(
    "field, msg, type, loc",
    [
        (
            "tag",
            "Field required",
            "missing",
            ["body", "tag"],
        ),
        (
            "variables",
            "Field required",
            "missing",
            ["body", "variables"],
        ),
    ],
)
def test_negative_missing_field(
    client_auth,
    case: Case,
    field: str,
    msg: str,
    type: str,
    loc: list,
    payload: dict,
):

    new_payload = payload.copy()
    del new_payload[field]

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=new_payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    detail = resp.json()["detail"][0]

    assert detail["loc"] == loc
    assert detail["msg"] == msg
    assert detail["type"] == type


@pytest.mark.integration
@pytest.mark.parametrize(
    "value, msg, type",
    [
        (
            "s" * 31,
            "String should have at most 30 characters",
            "string_too_long",
        ),
        (
            "s" * 2,
            "String should have at least 3 characters",
            "string_too_short",
        ),
    ],
    ids=["tag_gt_30", "tag_lt_2"],
)
def test_negative_create_tag_validation(
    client_auth: TestClient,
    case: Case,
    value: str,
    msg: str,
    type: str,
    payload: dict,
):

    new_payload = payload.copy()
    new_payload["tag"] = value

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=new_payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == msg
    assert body["detail"][0]["type"] == type


@pytest.mark.integration
@pytest.mark.parametrize(
    "variables, msg, type, loc",
    [
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": "not_number",
                    },
                },
            },
            "Input should be a valid number, unable to parse string as a number",
            "float_parsing",
            ["body", "variables", 0, "dist", "params", "param1"],
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "params": {
                        "param1": "not_number",
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
                        "param1": "not_number",
                    },
                },
            },
            "Field required",
            "missing",
            ["body", "variables", 0, "name"],
        ),
        (
            {
                "name": "E_i",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": "not_number",
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
            ["body", "variables", 0, "name"],
        ),
    ],
    ids=[
        "mean_not_number",
        "dist_name_missing",
        "variable_name_missing",
        "invalid_variable_name",
    ],
)
def test_negative_invalid_variables(
    client_auth: TestClient,
    case: Case,
    variables: dict,
    msg: str,
    type: str,
    loc: list,
):

    payload = {
        "tag": "case1",
        "variables": [variables],
    }

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"][0]

    assert detail["loc"] == loc
    assert detail["msg"] == msg
    assert detail["type"] == type


@pytest.mark.integration
@pytest.mark.parametrize(
    "corraletions, msg, type",
    [
        (
            {"E_c, poisson_c": "a"},
            "Input should be a valid number, unable to parse string as a number",
            "float_parsing",
        ),
        (
            {"E_c, poisson_c": 1.1},
            "Value error, Correlation 'E_c' is 1.1, it needs to be in range -1.0 and 1.0.",
            "value_error",
        ),
        (
            {"E_c, poisson_c": -1.1},
            "Value error, Correlation 'E_c' is -1.1, it needs to be in range -1.0 and 1.0.",
            "value_error",
        ),
    ],
    ids=[
        "mean_not_number",
        "value_gt_1",
        "value_lt_-1",
    ],
)
def test_negative_correlations_validation(
    client_auth: TestClient,
    case: Case,
    corraletions: dict,
    msg: str,
    type: str,
    payload: dict,
):

    payload_new = payload.copy()

    payload_new["correlations"] = corraletions

    resp = client_auth.post(app.url_path_for(ROUTE_NAME, case_id=case.id), json=payload_new)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"][0]

    assert detail["msg"] == msg
    assert detail["type"] == type


@pytest.mark.integration
def test_negative_create_variable_group_tag_name_must_be_unique_per_case(
    client_auth: TestClient,
    payload: dict,
    case: Case,
    variable_group: VariableGroup,
):

    resp = client_auth.post(
        app.url_path_for(ROUTE_NAME, case_id=case.id),
        json=payload,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = client_auth.post(
        app.url_path_for(ROUTE_NAME, case_id=case.id),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "Case Tag name shoud be unique per case."}


@pytest.mark.integration
def test_positive_create_two_case_can_have_the_same_variable_group_tag_name(
    client_auth: TestClient,
    session: Session,
    user: User,
    payload: dict,
):
    case1 = Case(tag="case1", user=user)
    case2 = Case(tag="case2", user=user)
    session.add_all([case1, case2])
    session.commit()

    resp = client_auth.post(
        app.url_path_for(ROUTE_NAME, case_id=case1.id),
        json=payload,
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp = client_auth.post(
        app.url_path_for(ROUTE_NAME, case_id=case2.id),
        json=payload,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    assert session.scalar(select(func.count()).select_from(Case)) == 2


@pytest.mark.integration
def test_negative_create_case_must_have_token(client: TestClient, case: Case):
    resp = client.get(app.url_path_for(ROUTE_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
