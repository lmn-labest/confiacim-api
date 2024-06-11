import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import User

faker = Faker()

ROUTE_NAME = "delete_user"


@pytest.mark.integration
def test_positive_delete_user(session, client: TestClient, user: User, token: str):

    resp = client.delete(
        app.url_path_for(ROUTE_NAME, user_id=user.id),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == status.HTTP_204_NO_CONTENT

    user_from_db = session.get(User, user.id)

    assert not user_from_db


@pytest.mark.integration
def test_negative_only_the_user_can_delete_himself(session, client: TestClient, user: User, other_user_token: str):

    resp = client.delete(
        app.url_path_for(ROUTE_NAME, user_id=user.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    user_from_db = session.get(User, user.id)

    assert user_from_db

    assert resp.json() == {"detail": "Not enough permissions"}


@pytest.mark.integration
def test_negative_user_must_have_token(session, client: TestClient, user: User):

    resp = client.delete(app.url_path_for(ROUTE_NAME, user_id=user.id))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    user_from_db = session.get(User, user.id)

    assert user_from_db

    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.integration
def test_negative_invalid_token(session, client: TestClient, user: User):

    resp = client.delete(
        app.url_path_for(ROUTE_NAME, user_id=user.id),
        headers={"Authorization": "Bearer INVALID_TOKEN"},
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    user_from_db = session.get(User, user.id)

    assert user_from_db

    assert resp.json() == {"detail": "Not authenticated"}
