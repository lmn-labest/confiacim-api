import pytest

from confiacim_api.database import Session
from confiacim_api.models import (
    Case,
    FormResult,
    ResultStatus,
    TencimResult,
    User,
)
from confiacim_api.system_stats import (
    count_case_with_simulation_success,
    count_tasks,
    total_success_simulations,
)


@pytest.mark.unit
def test_count_tasks():

    inspector_active_return = {
        "celery@c92af67035de": [
            {
                "id": "5bbca3cd-8190-463b-ae0e-11343cd18a59",
                "name": "confiacim_api.tasks.tencim_standalone_run",
                "args": [],
                "kwargs": {"result_id": 286, "rc_limit": False},
                "type": "confiacim_api.tasks.tencim_standalone_run",
                "hostname": "celery@c92af67035de",
                "time_start": 1731105964.97709,
                "acknowledged": True,
                "delivery_info": {"exchange": "", "routing_key": "celery", "priority": 0, "redelivered": False},
                "worker_pid": 104,
            },
            {
                "id": "62386b32-7394-45c8-9ad5-b0a32cc84e1d",
                "name": "confiacim_api.tasks.tencim_standalone_run",
                "args": [],
                "kwargs": {"result_id": 285, "rc_limit": False},
                "type": "confiacim_api.tasks.tencim_standalone_run",
                "hostname": "celery@c92af67035de",
                "time_start": 1731105964.5540097,
                "acknowledged": True,
                "delivery_info": {"exchange": "", "routing_key": "celery", "priority": 0, "redelivered": False},
                "worker_pid": 103,
            },
        ]
    }

    assert count_tasks(inspector_active_return) == 2


@pytest.mark.unit
def test_total_success_simulations(session: Session, user: User):

    case_1 = Case(tag="case1", user=user)
    case_2 = Case(tag="case2", user=user)

    results = [
        FormResult(
            case=case_1,
            status=ResultStatus.SUCCESS,
        ),
        # não deve ser considerado por causa do status
        FormResult(
            case=case_1,
            status=ResultStatus.CREATED,
        ),
        FormResult(
            case=case_2,
            status=ResultStatus.SUCCESS,
        ),
        TencimResult(
            case=case_2,
            status=ResultStatus.SUCCESS,
        ),
    ]
    session.add_all(results)
    session.commit()

    assert total_success_simulations(session) == 3


@pytest.mark.unit
def test_count_case_with_simulation_success(session: Session, user: User):
    """Queremos apenas saber o numero de casos que tem plenos menos uma simulação com status de
    sucesso."""

    case_1 = Case(tag="case1", user=user)
    case_2 = Case(tag="case2", user=user)

    results = [
        FormResult(
            case=case_1,
            status=ResultStatus.SUCCESS,
        ),
        # não deve ser considerado por causa do status
        FormResult(
            case=case_1,
            status=ResultStatus.CREATED,
        ),
        # FormResult e TencimResult deve ser considerado apenas uma vez por caso
        TencimResult(
            case=case_1,
            status=ResultStatus.SUCCESS,
        ),
        FormResult(
            case=case_2,
            status=ResultStatus.SUCCESS,
        ),
        # Mesmo caso deve ser condado apenas um vezes
        FormResult(
            case=case_2,
            status=ResultStatus.SUCCESS,
        ),
    ]
    session.add_all(results)
    session.commit()

    assert count_case_with_simulation_success(session) == 2
