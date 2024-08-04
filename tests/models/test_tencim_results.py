from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, ResultStatus, TencimResult


@pytest.mark.integration
def test_create_case(session: Session, case: Case):

    istep = (1, 2, 3)
    t = (1.0, 2.0, 3.0)
    rankine_rc = (100.0, 90.0, 10.0)
    mohr_coulomb_rc = (100.0, 80.0, 30.0)

    new_result = TencimResult(
        case=case,
        istep=istep,
        t=t,
        rankine_rc=rankine_rc,
        mohr_coulomb_rc=mohr_coulomb_rc,
        status=ResultStatus.RUNNING,
    )
    session.add(new_result)
    session.commit()
    new_result_id = new_result.id
    case_id = case.id
    session.reset()

    result_from_db = session.get(TencimResult, new_result_id)

    assert result_from_db is not None

    assert result_from_db is not new_result  # Para evitar falso positivos

    assert result_from_db.id == new_result_id
    assert result_from_db.case.id == case_id
    assert result_from_db.t == t
    assert result_from_db.istep == istep
    assert result_from_db.rankine_rc == rankine_rc
    assert result_from_db.mohr_coulomb_rc == mohr_coulomb_rc
    assert result_from_db.status == ResultStatus.RUNNING

    assert result_from_db.created_at is not None
    assert isinstance(result_from_db.created_at, datetime)

    assert result_from_db.updated_at is not None
    assert isinstance(result_from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(tencim_results):
    assert str(tencim_results) == f"TencimResult(id={tencim_results.id}, case={tencim_results.case.tag})"
