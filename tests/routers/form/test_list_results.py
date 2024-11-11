import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import FormResult

ROUTE_NAME = "form_result_list"


@pytest.mark.integration
def test_positive_list(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(ROUTE_NAME, case_id=form_results.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    response_tencim_results = body["items"]

    assert body["total"] == 1

    assert response_tencim_results[0]["id"] == form_results.id
    assert response_tencim_results[0]["task_id"] == form_results.task_id
    assert response_tencim_results[0]["status"] == form_results.status.value if form_results.status else None
    assert response_tencim_results[0]["description"] == form_results.description
    assert response_tencim_results[0]["critical_point"] == form_results.critical_point
    assert response_tencim_results[0]["created_at"] == (
        form_results.created_at.isoformat() if form_results.created_at else None
    )
    assert response_tencim_results[0]["updated_at"] == (
        form_results.updated_at.isoformat() if form_results.updated_at else None
    )


@pytest.mark.integration
def test_positive_check_fields(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(ROUTE_NAME, case_id=form_results.case_id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    response_tencim_results = body["items"]

    assert body["total"] == 1

    fields = response_tencim_results[0].keys()

    exepected = {"id", "task_id", "status", "created_at", "updated_at", "critical_point", "description"}

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
    form_results: FormResult,
    other_user_token: str,
):

    url = app.url_path_for(ROUTE_NAME, case_id=form_results.case_id)

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
