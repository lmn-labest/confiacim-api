import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_VIEW_NAME = "download_case_file"


@pytest.mark.integration
def test_download_case(
    client_auth: TestClient,
    case_with_file: Case,
):
    url = app.url_path_for(ROUTE_VIEW_NAME, case_id=case_with_file.id)
    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "application/zip"
    assert resp.content == case_with_file.base_file


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient):

    url = app.url_path_for(ROUTE_VIEW_NAME, case_id=404)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_user_can_upload_their_own_cases(
    client: TestClient,
    case: Case,
    other_user_token,
):

    resp = client.get(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_upload_case_must_have_token(
    client: TestClient,
    case: Case,
):
    resp = client.get(app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_if_case_not_have_base_file_return_400(
    client_auth: TestClient,
    case: Case,
):
    resp = client_auth.get(app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "The case has no base file."}
