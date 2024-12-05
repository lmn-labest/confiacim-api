import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import VariableGroup

ROUTE_NAME = "variable_group_retrieve"


@pytest.mark.integration
def test_positive_retrieve(client_auth: TestClient, variable_group: VariableGroup):

    resp = client_auth.get(
        app.url_path_for(
            ROUTE_NAME,
            case_id=variable_group.case.id,
            variable_group_id=variable_group.id,
        ),
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == variable_group.id
    assert body["tag"] == variable_group.tag
    assert body["description"] == variable_group.description
    assert body["case"] == variable_group.case_id

    assert body["variables"] == variable_group.variables
    assert body["correlations"] == variable_group.correlations

    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.integration
def test_negative_view_user_can_only_see_owns_cases(
    client: TestClient,
    variable_group: VariableGroup,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(
            ROUTE_NAME,
            case_id=variable_group.case.id,
            variable_group_id=variable_group.id,
        ),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Variable Group not found"}


@pytest.mark.integration
def test_negative_retrive_variable_group_not_found(client_auth: TestClient, variable_group: VariableGroup):

    resp = client_auth.get(
        app.url_path_for(
            ROUTE_NAME,
            case_id=variable_group.case.id,
            variable_group_id=404,
        ),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Variable Group not found"}


@pytest.mark.integration
def test_negative_retrive_case_not_found(client_auth: TestClient, variable_group: VariableGroup):

    resp = client_auth.get(
        app.url_path_for(
            ROUTE_NAME,
            case_id=404,
            variable_group_id=variable_group.id,
        ),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Variable Group not found"}


@pytest.mark.integration
def test_negative_retrive_need_have_token(client: TestClient):

    resp = client.get(app.url_path_for(ROUTE_NAME, case_id=1, variable_group_id=1))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
