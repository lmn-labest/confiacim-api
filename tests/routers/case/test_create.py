import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from confiacim_api.app import app
from confiacim_api.models import Case, User

ROUTE_CREATE_NAME = "case_create"


@pytest.mark.integration
def test_positive_create(client_auth: TestClient, session, user: User):
    payload = {"tag": "case_1"}

    resp = client_auth.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_201_CREATED

    case_db = session.scalars(select(Case)).first()

    assert case_db.id
    assert case_db.tag == payload["tag"]
    assert case_db.user == user

    body = resp.json()

    assert body["id"] == case_db.id
    assert body["tag"] == case_db.tag
    assert body["user"] == case_db.id


@pytest.mark.integration
def test_negative_create_missing_tag(client_auth: TestClient, session):
    payload = {"tag1": "1"}

    resp = client_auth.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    case_db = session.scalars(select(Case)).first()

    assert not case_db

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "Field required"
    assert body["detail"][0]["type"] == "missing"


@pytest.mark.integration
def test_negative_create_missing_tag_must_be_lt_30(client_auth: TestClient, session):
    payload = {"tag": "s" * 31}

    resp = client_auth.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    case_db = session.scalars(select(Case)).first()

    assert not case_db

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "String should have at most 30 characters"
    assert body["detail"][0]["type"] == "string_too_long"


@pytest.mark.integration
def test_negative_create_tag_name_must_be_unique_per_user(
    client_auth: TestClient,
    case: Case,
):
    payload = {"tag": "case_1"}

    resp = client_auth.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "Case Tag name shoud be unique per user."}


@pytest.mark.integration
def test_positive_create_two_user_can_have_the_same_tag_name(
    client: TestClient,
    session,
    case: Case,
    other_user_token: str,
):
    payload = {"tag": "case_1"}

    resp = client.post(
        app.url_path_for(ROUTE_CREATE_NAME),
        json=payload,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert session.scalar(select(func.count()).select_from(Case)) == 2


@pytest.mark.integration
def test_negative_create_case_must_have_token(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_CREATE_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
