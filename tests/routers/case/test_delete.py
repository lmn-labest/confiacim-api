import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case, TencimResult

ROUTE_NAME = "case_delete"


@pytest.mark.integration
def test_positive_delete_case(client_auth: TestClient, session, case: Case):

    resp = client_auth.delete(
        app.url_path_for(ROUTE_NAME, case_id=case.id),
    )

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert session.get(Case, case.id) is None


@pytest.mark.integration
def test_positive_delete_the_case_should_delete_the_results(
    client_auth: TestClient,
    session,
    tencim_results: TencimResult,
):

    resp = client_auth.delete(
        app.url_path_for(ROUTE_NAME, case_id=tencim_results.case.id),
    )

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert session.get(Case, tencim_results.case.id) is None
    assert session.get(TencimResult, tencim_results.id) is None


@pytest.mark.integration
def test_negative_case_not_found(client_auth: TestClient, case: Case):

    url = app.url_path_for(ROUTE_NAME, case_id=404)

    resp = client_auth.delete(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Case not found"


@pytest.mark.integration
def test_negative_user_can_delete_only_their_own_cases(
    client: TestClient,
    case: Case,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_NAME, case_id=case.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found"}


@pytest.mark.integration
def test_negative_delete_case_need_have_token(client: TestClient):

    resp = client.delete(app.url_path_for(ROUTE_NAME, case_id=1))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
