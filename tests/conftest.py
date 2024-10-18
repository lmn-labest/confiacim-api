from typing import Generator

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from confiacim_api.app import app
from confiacim_api.conf import settings
from confiacim_api.database import database_url, get_session
from confiacim_api.models import (
    Base,
    Case,
    FormResult,
    MaterialsBaseCaseAverageProps,
    ResultStatus,
    TencimResult,
    User,
)
from confiacim_api.security import create_access_token, get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker("email")


class MaterialsFactory(factory.Factory):
    class Meta:
        model = MaterialsBaseCaseAverageProps

    E_c = factory.fuzzy.FuzzyFloat(low=1e6, high=1e10)
    poisson_c = factory.fuzzy.FuzzyFloat(low=0, high=0.49)
    thermal_expansion_c = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    thermal_conductivity_c = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    volumetric_heat_capacity_c = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    friction_angle_c = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    cohesion_c = factory.fuzzy.FuzzyFloat(low=0, high=1e10)

    poisson_f = factory.fuzzy.FuzzyFloat(low=0, high=0.49)
    E_f = factory.fuzzy.FuzzyFloat(low=1e6, high=0.49)
    thermal_expansion_f = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    thermal_conductivity_f = factory.fuzzy.FuzzyFloat(low=0, high=1e10)
    volumetric_heat_capacity_f = factory.fuzzy.FuzzyFloat(low=0, high=1e10)


@pytest.fixture(scope="session")
def db_connection():

    engine = create_engine(f"{database_url}_test", echo=settings.SQLALCHEMY_ECHO)

    connection = engine.connect()

    Base.metadata.create_all(connection.engine)
    yield connection

    Base.metadata.drop_all(connection.engine)
    connection.close()
    engine.dispose()


@pytest.fixture
def session(db_connection):

    transaction = db_connection.begin()
    session = Session(bind=db_connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(db_session, transaction):

        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()


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
    return create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "admin": user.is_admin,
        }
    )


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
    return create_access_token(
        data={
            "sub": other_user.id,
            "email": other_user.email,
            "admin": other_user.is_admin,
        }
    )


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


@pytest.fixture
def case_with_file(session, user: User):
    case = Case(tag="case_1", user=user, base_file=b"Fake zip file.")
    session.add(case)
    session.commit()
    session.refresh(case)
    return case


@pytest.fixture
def case_with_materials_info(session, user: User):
    case = Case(tag="case_1", user=user)
    mat = MaterialsFactory(case=case)
    session.add_all([case, mat])
    session.commit()
    session.refresh(case)
    return case


@pytest.fixture
def case_with_real_file(session, user: User):
    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())
        session.add(case)
        session.commit()
        session.refresh(case)
    return case


@pytest.fixture
def case_form_with_real_file(session, user: User):
    with open("tests/fixtures/case_form.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())
        session.add(case)
        session.commit()
        session.refresh(case)
    return case


@pytest.fixture
def case_with_real_file_without_materials(session, user: User):
    with open("tests/fixtures/case_without_materials.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())
        session.add(case)
        session.commit()
        session.refresh(case)
    return case


@pytest.fixture
def tencim_results(session, case_with_real_file: Case):
    istep = (1, 2, 3)
    t = (1.0, 2.0, 3.0)
    rankine_rc = (100.0, 90.0, 10.0)
    mohr_coulomb_rc = (100.0, 80.0, 30.0)

    new_result = TencimResult(
        case=case_with_real_file,
        istep=istep,
        t=t,
        rankine_rc=rankine_rc,
        mohr_coulomb_rc=mohr_coulomb_rc,
        status=ResultStatus.SUCCESS,
        description="Descrição do caso",
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    return new_result


@pytest.fixture
def case_with_result(session, user: User):
    case = Case(tag="case1", user=user)
    result = TencimResult(case=case)
    session.add_all([case, result])
    session.commit()
    session.refresh(case)

    return case


@pytest.fixture
def materials(session: Session, case: Case):
    mat = MaterialsFactory(case_id=case.id)
    session.add(mat)
    session.commit()
    return mat


@pytest.fixture
def form_case_config():
    return {
        "variables": [
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
            {
                "name": "poisson_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
        ],
        "config": {
            "form": {
                "delta": 0.01,
                "tol": 1e-03,
                "maxit": 100,
            },
        },
    }


@pytest.fixture
def form_results(
    session,
    case_form_with_real_file: Case,
    form_case_config: dict,
):

    new_result = FormResult(
        case=case_form_with_real_file,
        status=ResultStatus.CREATED,
        config=form_case_config,
        description="Descrição do caso",
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    return new_result


@pytest.fixture
def form_results_with_critical_point(
    session,
    case_form_with_real_file: Case,
    form_case_config: dict,
):

    new_result = FormResult(
        case=case_form_with_real_file,
        status=ResultStatus.CREATED,
        config=form_case_config,
        critical_point=160,
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    return new_result
