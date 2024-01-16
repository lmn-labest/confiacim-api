from typing import Generator

import pytest
from confiacim_api.app import app
from confiacim_api.database import get_session
from confiacim_api.models import Base, Simulation
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    yield Session()
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
def simulation_list(session: Session):
    list_ = (
        Simulation(tag="simulation_1"),
        Simulation(tag="simulation_2"),
        Simulation(tag="simulation_3"),
    )

    session.bulk_save_objects(list_)

    session.commit()

    return session.scalars(select(Simulation)).all()
