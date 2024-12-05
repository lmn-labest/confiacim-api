import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import VariableGroup

ROUTE_NAME = "variable_group_delete"


@pytest.mark.integration
def test_positive_delete(
    client_auth: TestClient,
    session,
    variable_group: VariableGroup,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case.id,
        variable_group_id=variable_group.id,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert session.get(VariableGroup, variable_group.id) is None


@pytest.mark.integration
def test_negative_variable_group_not_found(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case_id,
        variable_group_id=404,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        variable_group_id=variable_group.id,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_user_can_delete_only_their_own_variable_groups(
    client: TestClient,
    variable_group: VariableGroup,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=variable_group.case.id,
        variable_group_id=variable_group.id,
    )

    resp = client.delete(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Variable Group/Case not found"


@pytest.mark.integration
def test_negative_delete_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, variable_group_id=1)

    resp = client.delete(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
