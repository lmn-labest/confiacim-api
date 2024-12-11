import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case, FormResult, ResultStatus

ROUTE_NAME = "form_result_error_retrieve"


@pytest.fixture
def form_results_with_error(
    session,
    case_form_with_real_file: Case,
    form_case_config: dict,
):

    new_result = FormResult(
        case=case_form_with_real_file,
        status=ResultStatus.CREATED,
        config=form_case_config,
        description="Descrição do caso",
        error="Algum erro",
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    return new_result


@pytest.mark.integration
def test_positive_retrieve(client_auth: TestClient, form_results_with_error: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results_with_error.case_id,
        result_id=form_results_with_error.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()
    assert body["error"] == "Algum erro"


@pytest.mark.integration
def test_negative_retrieve_result_not_found(client_auth: TestClient, form_results_with_error: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=form_results_with_error.case_id,
        result_id=404,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrieve_case_not_found(client_auth: TestClient, form_results_with_error: FormResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        result_id=form_results_with_error.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_retrieve_user_can_access_only_their_own_cases(
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
def test_negative_retrieve_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, result_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
