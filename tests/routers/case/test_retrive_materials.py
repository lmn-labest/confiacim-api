import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import Case

ROUTE_RETRIVE_NAME = "material_case_retrive"


@pytest.mark.integration
def test_positive_retrive(client_auth: TestClient, case_with_materials_info: Case):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case_with_materials_info.id))

    materials = case_with_materials_info.materials

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["id"] == materials.id
    assert body["E_c"] == materials.E_c
    assert body["E_f"] == materials.E_f
    assert body["poisson_c"] == materials.poisson_c
    assert body["poisson_f"] == materials.poisson_f

    assert body["created_at"] == (materials.created_at.isoformat() if materials.created_at is not None else None)
    assert body["updated_at"] == (materials.updated_at.isoformat() if materials.updated_at is not None else None)


@pytest.mark.integration
def test_negative_case_without_materials(client_auth: TestClient, case_with_file: Case):

    resp = client_auth.get(app.url_path_for(ROUTE_RETRIVE_NAME, case_id=case_with_file.id))

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "The case not have registered materials"}


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
