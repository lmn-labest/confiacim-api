import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case, HidrationPropInfos

ROUTE_RETRIEVE_NAME = "hidration_props_case_retrieve"


@pytest.mark.integration
def test_positive_retrieve(client_auth: TestClient, hidration_props: HidrationPropInfos):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIEVE_NAME, case_id=hidration_props.case_id))

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()
    assert body["id"] == hidration_props.id

    assert body["E_c_t"] == [6.0, 5.0]
    assert body["E_c_values"] == [60.0, 50.0]

    assert body["poisson_c_t"] == [1.0, 2.0, 3.0]
    assert body["poisson_c_values"] == [6.0, 5.0, 4.0]

    assert body["cohesion_c_t"] == [1.0]
    assert body["cohesion_c_values"] == [10.0]

    assert body["created_at"] == (
        hidration_props.created_at.isoformat() if hidration_props.created_at is not None else None
    )
    assert body["updated_at"] == (
        hidration_props.updated_at.isoformat() if hidration_props.updated_at is not None else None
    )


@pytest.mark.integration
def test_negative_case_without_hidration_props(client_auth: TestClient, case_with_file: Case):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIEVE_NAME, case_id=case_with_file.id))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "The case not have registered hidration props"}


@pytest.mark.integration
def test_negative_user_can_only_see_owns_cases(
    client: TestClient,
    hidration_props: HidrationPropInfos,
    other_user_token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_RETRIEVE_NAME, case_id=hidration_props.case_id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found"}


@pytest.mark.integration
def test_negative_retrieve_not_found(client_auth: TestClient):

    resp = client_auth.get(
        app.url_path_for(ROUTE_RETRIEVE_NAME, case_id=404),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    body = resp.json()

    assert body == {"detail": "Case not found"}


@pytest.mark.integration
def test_negative_retrieve_need_have_token(client: TestClient):

    resp = client.get(app.url_path_for(ROUTE_RETRIEVE_NAME, case_id=1))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
