import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case, VariableGroup

ROUTE_NAME = "variable_group_patch"


@pytest.fixture()
def payload():
    return {
        "tag": "case_2",
        "description": "Nova descrição",
        "variables": [
            {
                "name": "E_c",
                "dist": {
                    "name": "normal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.2,
                    },
                },
            },
            {
                "name": "poisson_c",
                "dist": {
                    "name": "normal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.15,
                    },
                },
            },
            {
                "name": "internal_pressure",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.1,
                    },
                },
            },
        ],
        "correlations": {
            "E_c, poisson_c": 0.3,
            "E_c, internal_pressure": 0.1,
        },
    }


@pytest.mark.integration
def test_positive_patch(
    client_auth: TestClient,
    session,
    variable_group: VariableGroup,
    payload: dict,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case.id,
        variable_group_id=variable_group.id,
    )

    resp = client_auth.patch(url, json=payload)

    assert resp.status_code == status.HTTP_200_OK
    from_db = session.get(VariableGroup, variable_group.id)

    assert from_db.tag == payload["tag"]
    assert from_db.description == payload["description"]
    assert from_db.variables == payload["variables"]
    assert from_db.correlations == payload["correlations"]


@pytest.mark.integration
def test_positive_patch_update_with_old_tag_name(
    client_auth: TestClient,
    session,
    variable_group: VariableGroup,
    payload: dict,
):

    payload = {"tag": variable_group.tag}

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case.id,
        variable_group_id=variable_group.id,
    )

    resp = client_auth.patch(url, json=payload)

    assert resp.status_code == status.HTTP_200_OK
    from_db = session.get(VariableGroup, variable_group.id)

    assert from_db.tag == payload["tag"]


@pytest.mark.integration
def test_positive_patch_tag_need_be_unique_per_case(
    client_auth: TestClient,
    session,
    payload: dict,
    case: Case,
    variables_form: list[dict],
):

    variable_group_a = VariableGroup(
        tag="group_a",
        case=case,
        variables=variables_form,
    )

    variable_group_b = VariableGroup(
        tag="group_b",
        case=case,
        variables=variables_form,
    )
    session.add_all([variable_group_a, variable_group_b])
    session.commit()

    payload = {"tag": "group_a"}

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group_b.case.id,
        variable_group_id=variable_group_b.id,
    )

    resp = client_auth.patch(url, json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json()["detail"] == "Variable Group Tag name shoud be unique per case."


@pytest.mark.integration
def test_negative_variable_group_correlation_needs_to_be_variables(
    client_auth: TestClient,
    variable_group: VariableGroup,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case_id,
        variable_group_id=variable_group.id,
    )

    payload = {
        "correlations": {
            "E_c, poisson_f": 0.3,
        }
    }

    resp = client_auth.patch(url, json=payload)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Correlation 'poisson_f' is not in the" in resp.json()["detail"]


@pytest.mark.integration
def test_negative_variable_group_not_found(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case_id,
        variable_group_id=404,
    )

    resp = client_auth.patch(url, json={})

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        variable_group_id=variable_group.id,
    )

    resp = client_auth.patch(url, json={})

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_user_can_patch_only_their_own_variable_groups(
    client: TestClient,
    variable_group: VariableGroup,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case.id,
        variable_group_id=variable_group.id,
    )

    resp = client.patch(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
        json={},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_patch_variable_groups_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, variable_group_id=1)

    resp = client.patch(url, json={})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
