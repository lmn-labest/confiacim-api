from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from confiacim_api.models import Simulation


def test_create_simulation(session: Session):
    new_simulation = Simulation(tag="simulation_1")
    session.add(new_simulation)
    session.commit()
    new_simulation_id = new_simulation.id
    session.reset()

    simulation_from_db = session.scalar(select(Simulation).where(Simulation.tag == "simulation_1"))

    assert simulation_from_db is not None

    assert simulation_from_db is not new_simulation  # Para evitar falso positivos

    assert simulation_from_db.tag == "simulation_1"
    assert simulation_from_db.id == new_simulation_id
    assert not simulation_from_db.celery_task_id


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


def test_str(simulation):
    assert str(simulation) == simulation.tag
