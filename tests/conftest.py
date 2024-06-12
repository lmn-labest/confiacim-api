from typing import Generator
from uuid import uuid4

import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from confiacim_api.app import app
from confiacim_api.conf import settings
from confiacim_api.database import database_url, get_session
from confiacim_api.models import Base, Simulation, User
from confiacim_api.security import create_access_token, get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker("email")


@pytest.fixture
def session():
    engine = create_engine(f"{database_url}_test", echo=settings.SQLALCHEMY_ECHO)
    Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
    Base.metadata.create_all(engine)
    with Session() as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def simulation(session: Session):
    new_simulation = Simulation(tag="simulation_1")
    session.add(new_simulation)
    session.commit()
    session.refresh(new_simulation)

    return new_simulation


@pytest.fixture
def outher_simulation(session: Session, simulation):
    new_simulation = Simulation(tag="simulation_2")
    session.add(new_simulation)
    session.commit()
    session.refresh(new_simulation)

    return new_simulation


@pytest.fixture
def simulation_list(session: Session):
    list_ = (
        Simulation(tag="simulation_1"),
        Simulation(tag="simulation_2", celery_task_id=uuid4()),
        Simulation(tag="simulation_3"),
    )

    session.bulk_save_objects(list_)

    session.commit()

    return session.scalars(select(Simulation)).all()


@pytest.fixture
def user_obj():
    password = "123456"
    user = UserFactory(password=get_password_hash(password))
    user.clean_password = password
    return user


@pytest.fixture
def user(session, user_obj):
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    return user_obj


@pytest.fixture
def token(user):
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def other_user(session, user_obj):

    password = "123456!!"
    user_obj = UserFactory(password=get_password_hash(password))

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    return user_obj


@pytest.fixture
def other_user_token(other_user):
    return create_access_token(data={"sub": other_user.email})


@pytest.fixture
def admin_user(session):
    password = "123456!!"
    user_obj = UserFactory(password=get_password_hash(password), is_admin=True)

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    return user_obj
