from io import BytesIO

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_VIEW_NAME = "upload_case_file"


@pytest.fixture
def zip_file_fake():
    return BytesIO(b"Fake zip file.")


@pytest.mark.integration
def test_upload_case(
    session,
    client_auth: TestClient,
    case: Case,
    mocker,
    zip_file_fake: BytesIO,
):
    is_zipfile_mocker = mocker.patch(
        "confiacim_api.routes.case.zipfile.is_zipfile",
        return_value=True,
    )

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_200_OK

    is_zipfile_mocker.assert_called_once()

    assert resp.json() == {"detail": "File upload success."}

    case_from_db = session.get(Case, case.id)

    assert case_from_db.base_file == b"Fake zip file."


@pytest.mark.integration
def test_negative_upload_case_must_be_a_zipfile(
    client_auth: TestClient,
    case: Case,
    mocker,
    zip_file_fake: BytesIO,
):
    is_zipfile_mocker = mocker.patch(
        "confiacim_api.routes.case.zipfile.is_zipfile",
        return_value=False,
    )

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    is_zipfile_mocker.assert_called_once()

    assert resp.json() == {"detail": "The file must be a zip file."}


@pytest.mark.integration
def test_negative_case_not_found(
    client_auth: TestClient,
    zip_file_fake: BytesIO,
):
    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=404),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_user_can_upload_their_own_cases(
    client: TestClient,
    case: Case,
    zip_file_fake: BytesIO,
    other_user_token,
):
    resp = client.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_upload_case_must_have_token(
    client: TestClient,
    case: Case,
):
    resp = client.post(app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
