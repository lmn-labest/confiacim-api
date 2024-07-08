import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import User
from confiacim_api.security import create_access_token

ROUTE_NAME = "admin_list_users"


@pytest.fixture
def admin_token(admin_user: User):
    return create_access_token(data={"sub": admin_user.email})


@pytest.mark.integration
def test_list_user(
    client: TestClient,
    user: User,
    other_user: User,
    admin_user: User,
    admin_token,
):

    resp = client.get(
        app.url_path_for(ROUTE_NAME),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["count"] == 3

    results = body["results"]

    assert {"id": user.id, "email": user.email} in results
    assert {"id": other_user.id, "email": other_user.email} in results
    assert {"id": admin_user.id, "email": admin_user.email} in results


@pytest.mark.integration
@pytest.mark.parametrize(
    "role, count",
    [
        ("admin", 1),
        ("user", 2),
    ],
    ids=["admin", "user"],
)
def test_list_filter_by_role(
    client: TestClient,
    user: User,
    other_user: User,
    admin_user: User,
    role: str,
    count: int,
    admin_token,
):

    url = f"{app.url_path_for(ROUTE_NAME)}?role={role}"

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json()["count"] == count


@pytest.mark.integration
def test_negative_filter_by_invalid_role_must_return_400(
    client: TestClient,
    admin_token: str,
):

    url = f"{app.url_path_for(ROUTE_NAME)}?role=invalid"

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    assert resp.json()["detail"] == "Invalid role filter."


@pytest.mark.integration
def test_negative_only_admin_can_list_user(
    client: TestClient,
    user: User,
    other_user: User,
    token: str,
):

    resp = client.get(
        app.url_path_for(ROUTE_NAME),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not enough permissions"


@pytest.mark.integration
def test_negative_need_have_admin_token(client: TestClient):

    resp = client.get(app.url_path_for(ROUTE_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json()["detail"] == "Not authenticated"
