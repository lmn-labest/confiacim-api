import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from confiacim_api.app import app
from confiacim_api.models import User

faker = Faker()


@pytest.fixture
def payload():
    return {"email": faker.email(), "password": faker.password()}


@pytest.mark.integration
def test_positive_create_user(session, client: TestClient, payload):
    resp = client.post(app.url_path_for("create_user"), json=payload)

    assert resp.status_code == status.HTTP_201_CREATED

    user_from_db = session.scalar(select(User).where(User.email == payload["email"]))

    assert user_from_db

    body = resp.json()

    assert body["id"] == user_from_db.id
    assert body["email"] == user_from_db.email


@pytest.mark.integration
def test_negative_email_must_be_unique(client: TestClient, user):
    payload = {"email": user.email, "password": faker.password()}

    resp = client.post(app.url_path_for("create_user"), json=payload)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.integration
@pytest.mark.parametrize("field", ["email", "password"])
def test_negative_missing_fields(client: TestClient, payload, field):
    data = payload.copy()
    del data[field]

    resp = client.post(app.url_path_for("create_user"), json=data)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"][0] == {
        "type": "missing",
        "loc": ["body", field],
        "msg": "Field required",
        "input": data,
    }
