import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_LIST_NAME = "case_list"


@pytest.mark.integration
def test_positive_list_only_user_case(
    client: TestClient,
    case_list: list[Case],
    token: str,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    assert len(resp.json()["cases"]) == 2

    resp = client.get(
        app.url_path_for(ROUTE_LIST_NAME),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    assert len(resp.json()["cases"]) == 1


@pytest.mark.integration
def test_positive_check_fields(
    client_auth: TestClient,
    case_list: list[Case],
    token: str,
):

    resp = client_auth.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    cases = resp.json()["cases"]

    assert len(cases) == 2

    fields = cases[0].keys()

    exepected = {"id", "tag", "user", "tencim_results"}

    assert set(fields) == exepected


@pytest.mark.integration
def test_positive_list_case_empty(client_auth: TestClient, token: str):

    resp = client_auth.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_200_OK

    cases_list_from_api = resp.json()["cases"]

    assert len(cases_list_from_api) == 0


@pytest.mark.integration
def test_negative_list_case_must_have_token(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_LIST_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
