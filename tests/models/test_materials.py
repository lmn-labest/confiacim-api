from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, MaterialsBaseCaseAverageProps


@pytest.mark.integration
def test_create_materials(session: Session, case: Case):

    mat = MaterialsBaseCaseAverageProps(
        case=case,
        E_c=1.0,
        E_f=1.5,
        poisson_c=0.1,
        poisson_f=0.2,
    )
    session.add(mat)
    session.commit()
    mat_id = mat.id
    case_id = case.id
    session.reset()

    from_db = session.get(MaterialsBaseCaseAverageProps, mat_id)

    assert from_db is not None

    assert from_db is not mat  # Para evitar falso positivos

    assert from_db.id == mat_id
    assert from_db.case.id == case_id
    assert from_db.E_c == 1.0
    assert from_db.E_f == 1.5
    assert from_db.poisson_c == 0.1
    assert from_db.poisson_f == 0.2

    assert from_db.created_at is not None
    assert isinstance(from_db.created_at, datetime)

    assert from_db.updated_at is not None
    assert isinstance(from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(materials):
    expected = f"MaterialsBaseCaseAverageProps(id={materials.id}, case={materials.case.tag}, E_c={materials.E_c}, ...)"
    assert str(materials) == expected
