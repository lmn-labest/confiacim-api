from confiacim_api.models import Simulation
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_create_simulation(session: Session):
    new_simulation = Simulation(tag="simulation_1")
    session.add(new_simulation)
    session.commit()

    query = select(Simulation).where(Simulation.tag == "simulation_1")

    simulation_from_db = session.scalar(query)

    assert simulation_from_db is not None

    assert simulation_from_db.tag == new_simulation.tag
    assert simulation_from_db.id == new_simulation.id


def test_str(simulation):
    assert str(simulation) == simulation.tag
