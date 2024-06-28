from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from confiacim_api.models import Simulation, User
from confiacim_api.security import verify_password


@pytest.mark.unit
def test_model_instance_obj(user_obj):
    assert user_obj.id is None
    assert user_obj.email is not None
    assert user_obj.password is not None
    assert user_obj.is_admin is None
    assert user_obj.created_at is None
    assert user_obj.updated_at is None


@pytest.mark.unit
def test_model_repr(user):
    assert str(user) == f"User(email={user.email}, is_admin={user.is_admin})"


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


@pytest.mark.integration
def test_create_user_default_admin_value(session: Session):

    user = User(email="test@email.com", password="123456")

    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.is_admin is False


@pytest.mark.integration
def test_admin_user_must_have_is_admin_equal_to_true(admin_user: User):
    assert admin_user.is_admin is True


@pytest.mark.integration
def test_a_user_can_have_many_simulations(session: Session, user: User):
    simulation1 = Simulation(tag="simulation_1", user=user)
    simulation2 = Simulation(tag="simulation_2", user=user)

    session.add_all([simulation1, simulation2])
    session.commit()

    assert len(user.simulations) == 2
    assert simulation1 in user.simulations
    assert simulation2 in user.simulations
