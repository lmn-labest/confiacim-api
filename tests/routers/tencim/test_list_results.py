import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import TencimResult

ROUTE_NAME = "tencim_result_list"


@pytest.mark.integration
def test_positive_list(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(ROUTE_NAME, case_id=tencim_results.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    response_tencim_results = body["results"]

    assert len(response_tencim_results) == 1

    assert response_tencim_results[0]["id"] == tencim_results.id
    assert response_tencim_results[0]["task_id"] == tencim_results.task_id
    assert response_tencim_results[0]["status"] == tencim_results.status.value if tencim_results.status else None
    assert response_tencim_results[0]["created_at"] == (
        tencim_results.created_at.isoformat() if tencim_results.created_at else None
    )
    assert response_tencim_results[0]["updated_at"] == (
        tencim_results.updated_at.isoformat() if tencim_results.updated_at else None
    )


@pytest.mark.integration
def test_positive_check_fields(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(ROUTE_NAME, case_id=tencim_results.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    response_tencim_results = body["results"]

    assert len(response_tencim_results) == 1

    fields = response_tencim_results[0].keys()

    exepected = {"id", "task_id", "status", "created_at", "updated_at"}

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
    tencim_results: TencimResult,
    other_user_token: str,
):

    url = app.url_path_for(ROUTE_NAME, case_id=tencim_results.case_id)

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
