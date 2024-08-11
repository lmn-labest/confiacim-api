import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_RETRIVE_NAME = "case_retrive"


@pytest.mark.integration
def test_positive_retrive(client_auth: TestClient, case_with_result: Case):

    resp = client_auth.get(
        app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case_with_result.id),
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == case_with_result.id
    assert body["tag"] == case_with_result.tag
    assert body["user"] == case_with_result.user.id
    assert body["tencim_result_ids"] == [
        {
            "id": case_with_result.tencim_results[0].id,
            "status": (
                case_with_result.tencim_results[0].status.value
                if case_with_result.tencim_results[0].status is not None
                else None
            ),
            "task_id": case_with_result.tencim_results[0].task_id,
            "created_at": (
                case_with_result.tencim_results[0].created_at.isoformat()
                if case_with_result.tencim_results[0].created_at is not None
                else None
            ),
            "updated_at": (
                case_with_result.tencim_results[0].updated_at.isoformat()
                if case_with_result.tencim_results[0].updated_at is not None
                else None
            ),
        }
    ]


@pytest.mark.integration
def test_negative_view_user_can_only_see_owns_cases(
    client: TestClient,
    case: Case,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found"}


@pytest.mark.integration
def test_negative_retrive_not_found(client: TestClient, token: str):

    resp = client.get(
        app.url_path_for(ROUTE_RETRIVE_NAME, case_id=404),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Case not found"}


@pytest.mark.integration
def test_negative_retrive_need_have_token(client: TestClient):

    resp = client.get(app.url_path_for(ROUTE_RETRIVE_NAME, case_id=1))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
