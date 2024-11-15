from io import BytesIO

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from confiacim_api.models import (
    Case,
    FormResult,
    MaterialsBaseCaseAverageProps,
    TencimResult,
    User,
)


@pytest.mark.integration
def test_create_case(session: Session, user: User):
    new_case = Case(tag="case1", user=user)
    session.add(new_case)
    session.commit()
    new_case_id = new_case.id
    user_id = user.id
    user_email = user.email
    session.reset()

    case_from_db = session.scalar(select(Case).where(Case.tag == "case1"))

    assert case_from_db is not None

    assert case_from_db is not new_case  # Para evitar falso positivos

    assert case_from_db.tag == "case1"
    assert case_from_db.id == new_case_id
    assert case_from_db.user_id == user_id
    assert case_from_db.user.email == user_email


@pytest.mark.unit
def test_str(case):
    assert str(case) == f"Case(id={case.id}, case={case.tag})"


@pytest.mark.integration
def test_model_create_two_user_can_have_the_same_tag_name(
    session,
    user: User,
    other_user: User,
):
    case_user = Case(tag="case1", user=user)
    case_other_user = Case(tag="case1", user=other_user)

    session.add_all([case_user, case_other_user])
    session.commit()

    assert case_user.id is not None
    assert case_other_user.id is not None


@pytest.mark.integration
def test_model_create_tag_name_must_be_unique_per_user(
    session,
    user: User,
):
    case1 = Case(tag="case1", user=user)
    case2 = Case(tag="case1", user=user)

    session.add_all([case1, case2])
    with pytest.raises(IntegrityError) as e:
        session.commit()

    assert "case_tag_user" in e.value.args[0]


@pytest.mark.integration
def test_save_blob_in_model(session, user: User):
    case = Case(tag="case1", user=user)

    assert case.base_file is None

    file = BytesIO(b"File Like")
    case.base_file = file.read()

    session.add(case)
    session.commit()
    session.reset()

    case_from_db = session.scalar(select(Case).where(Case.tag == "case1"))

    assert case_from_db.base_file == b"File Like"


@pytest.mark.integration
def test_case_can_have_many_tencim_results(session: Session, case: Case):

    values = {
        "istep": (1, 2, 3),
        "t": (1.0, 2.0, 3.0),
        "rankine_rc": (100.0, 90.0, 10.0),
        "mohr_coulomb_rc": (100.0, 80.0, 30.0),
    }

    result1 = TencimResult(case=case, **values)
    result2 = TencimResult(case=case, **values)

    session.add_all([result1, result2])
    session.commit()

    assert len(case.tencim_results) == 2
    assert result1 in case.tencim_results
    assert result2 in case.tencim_results


@pytest.mark.integration
def test_case_can_have_many_form_results(session: Session, case: Case):

    result1 = FormResult(case=case)
    result2 = FormResult(case=case)

    session.add_all([result1, result2])
    session.commit()

    assert len(case.form_results) == 2
    assert result1 in case.form_results
    assert result2 in case.form_results


@pytest.mark.integration
def test_case_can_have_one_materials(session: Session, case: Case, materials: MaterialsBaseCaseAverageProps):

    assert case.materials == materials


@pytest.mark.integration
def test_deleting_the_case_should_delete_the_materials(
    session: Session, case: Case, materials: MaterialsBaseCaseAverageProps
):
    """Testa a configuracao do cascate"""

    session.delete(case)
    session.commit()

    assert session.get(Case, case.id) is None
    assert session.get(MaterialsBaseCaseAverageProps, materials.id) is None


@pytest.mark.integration
def test_deleting_the_case_should_delete_the_form_results(session: Session, case: Case):
    """Testa a configuracao do cascate"""

    session.add(FormResult(case=case))
    session.commit()

    session.delete(case)
    session.commit()

    assert session.scalar(select(func.count()).select_from(FormResult)) == 0


@pytest.mark.integration
def test_deleting_the_case_should_delete_the_tencim_results(session: Session, case: Case):
    """Testa a configuracao do cascate"""

    values = {
        "istep": (1, 2, 3),
        "t": (1.0, 2.0, 3.0),
        "rankine_rc": (100.0, 90.0, 10.0),
        "mohr_coulomb_rc": (100.0, 80.0, 30.0),
    }

    session.add(TencimResult(case=case, **values))
    session.commit()

    session.delete(case)
    session.commit()

    assert session.scalar(select(func.count()).select_from(TencimResult)) == 0
