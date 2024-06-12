import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.security import create_access_token

ROUTE_NAME = "admin_list_users"


@pytest.mark.integration
def test_list_user(client: TestClient, user, other_user, admin_user):

    token = create_access_token(data={"sub": admin_user.email})

    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["count"] == 2
    assert body["results"][0] == {
        "id": user.id,
        "email": user.email,
    }
    assert body["results"][1] == {
        "id": other_user.id,
        "email": other_user.email,
    }


@pytest.mark.integration
def test_negative_only_admin_can_list_user(client: TestClient, user, other_user):

    token = create_access_token(data={"sub": user.email})

    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not enough permissions"


@pytest.mark.integration
def test_negative_need_have_admin_token(client: TestClient):

    resp = client.get(app.url_path_for(ROUTE_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
