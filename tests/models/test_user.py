from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from confiacim_api.models import User
from confiacim_api.security import verify_password


@pytest.mark.unit
def test_model_instance_obj(user_obj):
    assert user_obj.id is None
    assert user_obj.email is not None
    assert user_obj.password is not None
    assert user_obj.created_at is None
    assert user_obj.updated_at is None


@pytest.mark.unit
def test_model_repr(user_obj):
    assert str(user_obj) == f"User(email={user_obj.email})"


@pytest.mark.integration
def test_create_user(session: Session, user_obj: User):
    email = user_obj.email
    password = user_obj.clean_password  # type: ignore[attr-defined]

    session.add(user_obj)
    session.commit()
    session.reset()

    user_from_db = session.scalar(select(User))

    assert user_from_db is not None
    assert user_from_db is not user_obj

    assert user_from_db.email == email
    assert verify_password(password, user_from_db.password)

    assert user_from_db.created_at is not None
    assert isinstance(user_from_db.created_at, datetime)

    assert user_from_db.updated_at is not None
    assert isinstance(user_from_db.updated_at, datetime)
