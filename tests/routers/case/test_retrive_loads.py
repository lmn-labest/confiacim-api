import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_RETRIVE_NAME = "loads_case_retrive"


@pytest.mark.integration
def test_positive_retrive(client_auth: TestClient, case_with_loads_info: Case):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case_with_loads_info.id))

    loads = case_with_loads_info.loads

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == loads.id
    assert body["nodalsource"] == loads.nodalsource

    for i in range(3):
        assert body["mechanical_istep"][i] == loads.mechanical_istep[i] if loads.mechanical_istep else None
        assert body["mechanical_force"][i] == loads.mechanical_force[i] if loads.mechanical_force else None

    for i in range(2):
        assert body["thermal_istep"][i] == loads.thermal_istep[i] if loads.thermal_istep else None
        assert body["thermal_h"][i] == loads.thermal_h[i] if loads.thermal_h else None
        assert body["thermal_temperature"][i] == loads.thermal_temperature[i] if loads.thermal_temperature else None

    assert body["created_at"] == (loads.created_at.isoformat() if loads.created_at is not None else None)
    assert body["updated_at"] == (loads.updated_at.isoformat() if loads.updated_at is not None else None)


@pytest.mark.integration
def test_negative_case_without_loads(client_auth: TestClient, case_with_file: Case):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case_with_file.id))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "The case not have registered loads"}


@pytest.mark.integration
def test_negative_user_can_only_see_owns_cases(
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
