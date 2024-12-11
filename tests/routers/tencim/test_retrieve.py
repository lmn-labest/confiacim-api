import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import TencimResult

ROUTE_NAME = "tencim_result_retrieve"


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

    assert body["id"] == tencim_results.id
    assert body["task_id"] == tencim_results.task_id
    assert body["istep"] == list(tencim_results.istep) if tencim_results.istep else ""
    assert body["t"] == list(tencim_results.t) if tencim_results.t else ""
    assert body["rankine_rc"] == list(tencim_results.rankine_rc) if tencim_results.rankine_rc else ""
    assert body["mohr_coulomb_rc"] == list(tencim_results.mohr_coulomb_rc) if tencim_results.mohr_coulomb_rc else ""
    assert body["critical_point"] == tencim_results.critical_point
    assert body["rc_limit"] == tencim_results.rc_limit
    assert body["error"] == tencim_results.error
    assert body["status"] == tencim_results.status.value if tencim_results.status else None
    assert body["description"] == tencim_results.description
    assert body["created_at"] == (tencim_results.created_at.isoformat() if tencim_results.created_at else None)
    assert body["updated_at"] == (tencim_results.updated_at.isoformat() if tencim_results.updated_at else None)


@pytest.mark.integration
def test_positive_check_fields(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case_id,
        result_id=tencim_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json().keys()

    exepected = {
        "id",
        "task_id",
        "istep",
        "t",
        "rankine_rc",
        "mohr_coulomb_rc",
        "error",
        "status",
        "critical_point",
        "rc_limit",
        "description",
        "created_at",
        "updated_at",
    }

    assert set(body) == exepected


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
