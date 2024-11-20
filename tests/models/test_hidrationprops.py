from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, HidrationPropInfos


@pytest.mark.integration
def test_create_hidrationprops(session: Session, case: Case):

    mat = HidrationPropInfos(
        case=case,
        E_c_t=(1.0, 2.0),
        E_c_values=(10.0, 20.0),
        poisson_c_t=(5.0,),
        poisson_c_values=(10.0,),
        cohesion_c_t=(1.0, 2.0, 4.0),
        cohesion_c_values=(30.0, 20.0, 40.0),
    )
    session.add(mat)
    session.commit()
    mat_id = mat.id
    case_id = case.id
    session.reset()

    from_db = session.get(HidrationPropInfos, mat_id)

    assert from_db is not None

    assert from_db is not mat  # Para evitar falso positivos

    assert from_db.id == mat_id
    assert from_db.case.id == case_id

    assert from_db.E_c_t == (1.0, 2.0)
    assert from_db.E_c_values == (10.0, 20.0)

    assert from_db.poisson_c_t == (5.0,)
    assert from_db.poisson_c_values == (10.0,)

    assert from_db.cohesion_c_t == (1.0, 2.0, 4.0)
    assert from_db.cohesion_c_values == (30.0, 20.0, 40.0)

    assert from_db.created_at is not None
    assert isinstance(from_db.created_at, datetime)

    assert from_db.updated_at is not None
    assert isinstance(from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(hidration_props):
    expected = f"HidrationPropInfos(id={hidration_props.id}, case={hidration_props.case.tag}, ...)"
    assert str(hidration_props) == expected
