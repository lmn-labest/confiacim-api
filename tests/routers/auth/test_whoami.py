import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from confiacim_api.app import app
from confiacim_api.models import User
from confiacim_api.security import create_access_token

ROUTE_NAME = "whoiam"

faker = Faker()


@pytest.mark.integration
def test_positive_whoiam(client: TestClient, user: User, token: str):
    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["email"] == user.email


@pytest.mark.integration
def test_negative_whoiam_user_not_exists(client: TestClient):
    token = create_access_token(
        data={
            "sub": 1,
            "email": faker.email(),
            "admin": False,
        }
    )

    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_whoiam_invalid_token(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": "Bearer invalid_token"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_whoiam_expired_token(client: TestClient, user):
    with freeze_time("2012-01-14 01:00:00"):
        token = create_access_token(data={"sub": user.email})

    with freeze_time("2012-01-14 02:00:00"):
        resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_whoiam_wrong_id(client: TestClient, user: User):

    token = create_access_token(
        data={
            "sub": user.id + 1,
            "email": user.email,
            "admin": user.is_admin,
        }
    )

    resp = client.get(app.url_path_for(ROUTE_NAME), headers={"Authorization": token})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Not authenticated"}
