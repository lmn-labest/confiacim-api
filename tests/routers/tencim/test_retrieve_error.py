import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import TencimResult

ROUTE_NAME = "tencim_result_error_retrieve"


@pytest.mark.integration
def test_positive_retrieve(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case_id,
        result_id=tencim_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["error"] == tencim_results.error


@pytest.mark.integration
def test_negative_retrieve_result_not_found(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case_id,
        result_id=404,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrieve_case_not_found(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        result_id=tencim_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrieve_user_can_access_only_their_own_cases(
    client: TestClient,
    tencim_results: TencimResult,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case.id,
        result_id=tencim_results.id,
    )

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrieve_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, result_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
