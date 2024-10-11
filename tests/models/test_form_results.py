from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, FormResult, ResultStatus


@pytest.mark.integration
def test_create_form_result(session: Session, case: Case):

    new_result = FormResult(
        case=case,
        status=ResultStatus.RUNNING,
        description="Descrição do Resultado",
        beta=1.0,
        resid=1e-3,
        it=3,
        Pf=1e-5,
        critical_point=12,
    )
    session.add(new_result)
    session.commit()
    new_result_id = new_result.id
    case_id = case.id
    session.reset()

    result_from_db = session.get(FormResult, new_result_id)

    assert result_from_db is not None

    assert result_from_db is not new_result  # Para evitar falso positivos

    assert result_from_db.id == new_result_id
    assert result_from_db.case.id == case_id
    assert result_from_db.beta == pytest.approx(1.0)
    assert result_from_db.resid == pytest.approx(1e-3)
    assert result_from_db.it == 3
    assert result_from_db.critical_point == 12
    assert result_from_db.Pf == pytest.approx(1e-5)
    assert result_from_db.status == ResultStatus.RUNNING
    assert result_from_db.description == "Descrição do Resultado"

    assert result_from_db.config is None
    assert result_from_db.variables_stats is None

    assert result_from_db.created_at is not None
    assert isinstance(result_from_db.created_at, datetime)

    assert result_from_db.updated_at is not None
    assert isinstance(result_from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(form_results):
    assert str(form_results) == f"FormResult(id={form_results.id}, case={form_results.case.tag})"
