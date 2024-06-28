from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from confiacim_api.models import Simulation, User


@pytest.mark.integration
def test_create_simulation(session: Session, user: User):
    new_simulation = Simulation(tag="simulation_1", user=user)
    session.add(new_simulation)
    session.commit()
    new_simulation_id = new_simulation.id
    user_id = user.id
    user_email = user.email
    session.reset()

    simulation_from_db = session.scalar(select(Simulation).where(Simulation.tag == "simulation_1"))

    assert simulation_from_db is not None

    assert simulation_from_db is not new_simulation  # Para evitar falso positivos

    assert simulation_from_db.tag == "simulation_1"
    assert simulation_from_db.id == new_simulation_id
    assert simulation_from_db.user_id == user_id
    assert simulation_from_db.user.email == user_email
    assert not simulation_from_db.celery_task_id


@pytest.mark.integration
def test_set_celery_task(session, simulation):
    task_uuid = uuid4()

    simulation.celery_task_id = task_uuid
    id_ = simulation.id
    session.add(simulation)
    session.commit()
    session.reset()

    simulation_from_db = session.scalar(select(Simulation).where(Simulation.id == id_))

    assert simulation_from_db is not simulation  # Para evitar falso positivos
    assert simulation_from_db.celery_task_id == task_uuid


@pytest.mark.unit
def test_str(simulation):
    assert str(simulation) == simulation.tag
