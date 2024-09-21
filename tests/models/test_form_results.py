from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, ResultStatus, TencimResult


@pytest.mark.integration
def test_create_case(session: Session, case: Case):

    new_result = TencimResult(
        case=case,
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
    assert result_from_db.status == ResultStatus.RUNNING

    assert result_from_db.created_at is not None
    assert isinstance(result_from_db.created_at, datetime)

    assert result_from_db.updated_at is not None
    assert isinstance(result_from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(form_results):
    assert str(form_results) == f"FormResult(id={form_results.id}, case={form_results.case.tag})"
