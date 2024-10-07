import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import FormResult

ROUTE_NAME = "form_result_retrive"


@pytest.mark.integration
def test_positive_retrive(
    client_auth: TestClient,
    form_results_with_critical_point: FormResult,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results_with_critical_point.case_id,
        result_id=form_results_with_critical_point.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == form_results_with_critical_point.id
    assert body["task_id"] == form_results_with_critical_point.task_id
    assert body["critical_point"] == form_results_with_critical_point.critical_point
    assert body["beta"] == form_results_with_critical_point.beta
    assert body["resid"] == form_results_with_critical_point.resid
    assert body["it"] == form_results_with_critical_point.it
    assert body["Pf"] == form_results_with_critical_point.Pf
    assert body["config"] == form_results_with_critical_point.config

    assert body["error"] == form_results_with_critical_point.error
    assert body["status"] == (
        form_results_with_critical_point.status.value if form_results_with_critical_point.status else None
    )
    assert body["created_at"] == (
        form_results_with_critical_point.created_at.isoformat() if form_results_with_critical_point.created_at else None
    )
    assert body["updated_at"] == (
        form_results_with_critical_point.updated_at.isoformat() if form_results_with_critical_point.updated_at else None
    )


@pytest.mark.integration
def test_positive_check_fields(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case_id,
        result_id=form_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json().keys()

    exepected = {
        "id",
        "task_id",
        "critical_point",
        "beta",
        "resid",
        "it",
        "Pf",
        "config",
        "error",
        "status",
        "created_at",
        "updated_at",
    }

    assert set(body) == exepected


@pytest.mark.integration
def test_negative_retrive_result_not_found(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case_id,
        result_id=404,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrive_case_not_found(client_auth: TestClient, form_results: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        result_id=form_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrive_user_can_access_only_their_own_cases(
    client: TestClient,
    form_results: FormResult,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results.case.id,
        result_id=form_results.id,
    )

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrive_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, result_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
