import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import FormResult

ROUTE_NAME = "form_result_delete"


@pytest.mark.integration
def test_positive_delete(
    client_auth: TestClient,
    session,
    form_results: FormResult,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case_id,
        result_id=form_results.id,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert session.get(FormResult, form_results.id) is None


@pytest.mark.integration
def test_negative_result_not_found(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case_id,
        result_id=404,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        result_id=form_results.id,
    )

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_user_can_delete_only_their_own_cases(
    client: TestClient,
    form_results: FormResult,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case.id,
        result_id=form_results.id,
    )

    resp = client.delete(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_delete_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, result_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
