import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from confiacim_api.models import Case, User


@pytest.mark.integration
def test_create_case(session: Session, user: User):
    new_case = Case(tag="case1", user=user)
    session.add(new_case)
    session.commit()
    new_case_id = new_case.id
    user_id = user.id
    user_email = user.email
    session.reset()

    simulation_from_db = session.scalar(select(Case).where(Case.tag == "case1"))

    assert simulation_from_db is not None

    assert simulation_from_db is not new_case  # Para evitar falso positivos

    assert simulation_from_db.tag == "case1"
    assert simulation_from_db.id == new_case_id
    assert simulation_from_db.user_id == user_id
    assert simulation_from_db.user.email == user_email


@pytest.mark.unit
def test_str(case):
    assert str(case) == case.tag
