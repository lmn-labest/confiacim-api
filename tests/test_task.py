import pytest
from confiacim.erros import TencimRunError
from sqlalchemy import select

from confiacim_api.models import Case, ResultStatus, TencimResult, User
from confiacim_api.tasks import TaskFileCaseNotFound, tencim_standalone_run


@pytest.fixture
def session_factory(mocker, session):
    return mocker.patch("confiacim_api.tasks.SessionFactory", return_value=session)


@pytest.fixture
def case_fail(session, user: User):
    with open("tests/fixtures/case_fail.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())
        session.add(case)
        session.commit()
        session.refresh(case)
    return case


@pytest.mark.slow
@pytest.mark.integration
def test_positive_tencim_standalone_run(
    case_with_real_file: Case,
    session_factory,
    mocker,
    tmp_path,
):

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)
    task_return = tencim_standalone_run(case_with_real_file.id)

    assert "results_id" in task_return

    with session_factory() as session:
        result_from_db = session.get(TencimResult, task_return["results_id"])

    assert result_from_db is not None
    assert result_from_db.status == ResultStatus.SUCCESS


@pytest.mark.integration
def test_negative_tencim_standalone_run_tencim_error(
    case_fail: Case,
    session_factory,
    mocker,
    tmp_path,
):
    case_id = case_fail.id
    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)

    with pytest.raises(TencimRunError):
        tencim_standalone_run(case_id)

    with session_factory() as session:
        result_from_db = session.scalar(select(TencimResult).where(TencimResult.case_id == case_id))

    assert "ERROR STOP 1" in result_from_db.error
    assert result_from_db.status == ResultStatus.FAILED


@pytest.mark.integration
def test_negative_tencim_standalone_run_file_not_found(session_factory):

    with pytest.raises(TaskFileCaseNotFound, match="Case files not found."):
        tencim_standalone_run(404)
