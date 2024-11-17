from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, LoadsBaseCaseInfos


@pytest.mark.integration
def test_create_loads(session: Session, case: Case):

    mat = LoadsBaseCaseInfos(
        case=case,
        nodalsource=1.0,
        #
        mechanical_istep=(1, 2, 3),
        mechanical_force=(10.0, 20.0, 30.0),
        #
        thermal_istep=(1, 2),
        thermal_h=(5.0, 5.0),
        thermal_temperature=(35.0, 45.0),
    )
    session.add(mat)
    session.commit()
    mat_id = mat.id
    case_id = case.id
    session.reset()

    from_db = session.get(LoadsBaseCaseInfos, mat_id)

    assert from_db is not None

    assert from_db is not mat  # Para evitar falso positivos

    assert from_db.id == mat_id
    assert from_db.case.id == case_id

    assert from_db.nodalsource == 1.0

    assert from_db.mechanical_istep == (1, 2, 3)
    assert from_db.mechanical_force == (10.0, 20.0, 30.0)

    assert from_db.thermal_istep == (1, 2)
    assert from_db.thermal_h == (5.0, 5.0)
    assert from_db.thermal_temperature == (35.0, 45.0)

    assert from_db.created_at is not None
    assert isinstance(from_db.created_at, datetime)

    assert from_db.updated_at is not None
    assert isinstance(from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(loads):
    expected = f"LoadsBaseCaseInfos(id={loads.id}, case={loads.case.tag}, nodalsource={loads.nodalsource}, ...)"
    assert str(loads) == expected
