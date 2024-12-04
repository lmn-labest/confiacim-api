import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import VariableGroup

ROUTE_NAME = "variable_group_list"


@pytest.mark.integration
def test_positive_list(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(ROUTE_NAME, case_id=variable_group.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    variabel_groups_list = body["items"]

    assert body["total"] == 1

    assert variabel_groups_list[0]["id"] == variable_group.id

    assert variabel_groups_list[0]["tag"] == variable_group.tag
    assert variabel_groups_list[0]["description"] == variable_group.description
    assert variabel_groups_list[0]["case"] == variable_group.case_id

    assert variabel_groups_list[0]["variables"] == variable_group.variables
    assert variabel_groups_list[0]["correlations"] == variable_group.correlations

    assert variabel_groups_list[0]["created_at"] == (
        variable_group.created_at.isoformat() if variable_group.created_at else None
    )
    assert variabel_groups_list[0]["updated_at"] == (
        variable_group.updated_at.isoformat() if variable_group.updated_at else None
    )


@pytest.mark.integration
def test_positive_check_fields(client_auth: TestClient, variable_group: VariableGroup):

    url = app.url_path_for(ROUTE_NAME, case_id=variable_group.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    response_tencim_results = body["items"]

    assert body["total"] == 1

    fields = response_tencim_results[0].keys()

    exepected = {"id", "tag", "description", "case", "variables", "correlations", "created_at", "updated_at"}

    assert set(fields) == exepected


@pytest.mark.integration
def test_negative_list_case_not_found(client_auth: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=404)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Case not found"


@pytest.mark.integration
def test_negative_list_user_can_access_only_their_own_cases(
    client: TestClient,
    variable_group: VariableGroup,
    other_user_token: str,
):

    url = app.url_path_for(ROUTE_NAME, case_id=variable_group.case_id)

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Case not found"


@pytest.mark.integration
def test_negative_list_result_must_have_token(client: TestClient):
    url = app.url_path_for(ROUTE_NAME, case_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
