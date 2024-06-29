from typing import Generator

import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from confiacim_api.app import app
from confiacim_api.conf import settings
from confiacim_api.database import database_url, get_session
from confiacim_api.models import Base, Case, User
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
def client_auth(session, token) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    headers = {"Authorization": f"Bearer {token}"}

    with TestClient(app, headers=headers) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


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


@pytest.fixture
def users(user, other_user, admin_user):
    return [user, other_user, admin_user]


@pytest.fixture
def case(session: Session, user: User):
    new_case = Case(tag="case_1", user=user)
    session.add(new_case)
    session.commit()
    session.refresh(new_case)

    return new_case


@pytest.fixture
def other_case(session: Session, case: Case, user: User):
    new_case = Case(tag="case_2", user=user)
    session.add(new_case)
    session.commit()
    session.refresh(new_case)

    return new_case


@pytest.fixture
def case_list(session: Session, user: User, other_user: User):
    list_ = (
        Case(tag="simulation_1", user=user),
        Case(tag="simulation_2", user=user),
        Case(tag="simulation_3", user=other_user),
    )

    # session.bulk_save_objects(list_)
    session.add_all(list_)

    session.commit()

    return session.scalars(select(Case)).all()
