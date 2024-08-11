import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from confiacim_api.app import app
from confiacim_api.conf import settings
from confiacim_api.security import ALGORITHM

ROUTE_NAME = "token"


@pytest.fixture
def payload(user):
    return {
        "username": user.email,
        "password": user.clean_password,
    }


@pytest.mark.integration
def test_positive_get_token(client: TestClient, payload):
    resp = client.post(app.url_path_for(ROUTE_NAME), data=payload)

    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()

    assert body["access_token"] is not None
    assert body["token_type"] == "bearer"


@pytest.mark.integration
def test_positive_token_verify_token(client: TestClient, user, payload):
    resp = client.post(app.url_path_for(ROUTE_NAME), data=payload)

    assert resp.status_code == status.HTTP_200_OK

    token = resp.json()["access_token"]

    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["exp"]
    assert payload["sub"] == user.id
    assert payload["email"] == user.email
    assert payload["admin"] == user.is_admin


@pytest.mark.integration
def test_negative_user_not_found(client: TestClient, payload):
    data = payload.copy()

    data["username"] = "notfound@email.com"

    resp = client.post(app.url_path_for(ROUTE_NAME), data=data)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Incorrect email or password"


@pytest.mark.integration
def test_negative_invalid_password(client: TestClient, payload):
    data = payload.copy()
    data["username"] += "wrong"

    resp = client.post(app.url_path_for(ROUTE_NAME), data=data)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Incorrect email or password"


@pytest.mark.integration
def test_negative_get_token_must_be_only_by_post(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_NAME))

    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert resp.json()["detail"] == "Method Not Allowed"


@pytest.mark.integration
def test_negative_token_must_expired_after_some_time(client: TestClient, payload):
    with freeze_time("2012-01-14 01:00:00"):
        resp = client.post(app.url_path_for(ROUTE_NAME), data=payload)
        assert resp.status_code == status.HTTP_200_OK
        token = resp.json()["access_token"]

    with freeze_time("2012-01-14 01:59:59"):
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])

    with freeze_time("2012-01-14 02:00:00"):
        with pytest.raises(jwt.ExpiredSignatureError):
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])


@pytest.mark.integration
@pytest.mark.parametrize("field", ["username", "password"])
def test_negative_missing_fields(client: TestClient, payload, field):
    data = payload.copy()
    data.pop(field)

    resp = client.post(app.url_path_for(ROUTE_NAME), data=data)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"][0] == {
        "type": "missing",
        "loc": ["body", field],
        "msg": "Field required",
        "input": None,
    }
