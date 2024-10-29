import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import FormResult

ROUTE_VIEW_NAME = "download_form_generated_case_file"


@pytest.mark.integration
def test_download_case(
    client_auth: TestClient,
    form_results_with_generated_case_files: FormResult,
):

    url = app.url_path_for(
        ROUTE_VIEW_NAME,
        case_id=form_results_with_generated_case_files.case.id,
        result_id=form_results_with_generated_case_files.id,
    )
    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "application/zip"
    assert resp.content == form_results_with_generated_case_files.generated_case_files


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient, form_results_with_generated_case_files: FormResult):

    url = app.url_path_for(ROUTE_VIEW_NAME, case_id=404, result_id=form_results_with_generated_case_files.id)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Result/Case not found."}


@pytest.mark.integration
def test_negative_result_not_found(client_auth: TestClient, form_results_with_generated_case_files: FormResult):

    url = app.url_path_for(ROUTE_VIEW_NAME, case_id=form_results_with_generated_case_files.case.id, result_id=404)

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Result/Case not found."}


@pytest.mark.integration
def test_negative_user_can_upload_their_own_cases(
    client: TestClient,
    form_results_with_generated_case_files: FormResult,
    other_user_token,
):

    resp = client.get(
        app.url_path_for(
            ROUTE_VIEW_NAME,
            case_id=form_results_with_generated_case_files.case.id,
            result_id=form_results_with_generated_case_files.id,
        ),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Result/Case not found."}


@pytest.mark.integration
def test_negative_upload_case_must_have_token(
    client: TestClient,
    form_results_with_generated_case_files: FormResult,
):
    resp = client.get(
        app.url_path_for(
            ROUTE_VIEW_NAME,
            case_id=form_results_with_generated_case_files.case.id,
            result_id=form_results_with_generated_case_files.id,
        )
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_if_case_not_have_generated_case_files_return_400(
    client_auth: TestClient,
    form_results: FormResult,
):
    resp = client_auth.get(
        app.url_path_for(
            ROUTE_VIEW_NAME,
            case_id=form_results.case.id,
            result_id=form_results.id,
        )
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "The form result has no generated case file."}
