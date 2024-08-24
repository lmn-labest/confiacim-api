import pytest
from confiacim.erros import TencimRunError

from confiacim_api.models import (
    Case,
    ResultStatus,
    TencimResult,
    User,
)
from confiacim_api.tasks import (
    ResultNotFound,
    TaskFileCaseNotFound,
    tencim_standalone_run,
)


@pytest.fixture
def session_factory(mocker, session):
    mocker.patch("confiacim_api.tasks.SessionFactory", return_value=session)
    return session


@pytest.fixture
def tencim_results_case_fail(session, user: User):
    with open("tests/fixtures/case_fail.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())

    result = TencimResult(case=case)
    session.add_all([case, result])
    session.commit()
    session.refresh(result)

    return result


@pytest.mark.slow
@pytest.mark.integration
def test_positive_tencim_standalone_run(
    tencim_results: TencimResult,
    session_factory,
    mocker,
    tmp_path,
):

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)
    tencim_standalone_run(tencim_results.id)

    with session_factory as session:
        result_from_db = session.get(TencimResult, tencim_results.id)

    assert result_from_db.status == ResultStatus.SUCCESS


@pytest.mark.slow
@pytest.mark.integration
def test_positive_tencim_standalone_run_rc_limit(
    tencim_results: TencimResult,
    session_factory,
    mocker,
    tmp_path,
):

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)
    tencim_standalone_run(tencim_results.id, rc_limit=True)

    with session_factory as session:
        result_from_db = session.get(TencimResult, tencim_results.id)

    assert result_from_db.status == ResultStatus.SUCCESS


@pytest.mark.integration
def test_negative_tencim_standalone_run_tencim_error(
    tencim_results_case_fail: Case,
    session_factory,
    mocker,
    tmp_path,
):

    result_id = tencim_results_case_fail.id
    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)

    with pytest.raises(TencimRunError):
        tencim_standalone_run(tencim_results_case_fail.id)

    with session_factory as session:
        result_from_db = session.get(TencimResult, result_id)

    assert "ERROR STOP 1" in result_from_db.error
    assert result_from_db.status == ResultStatus.FAILED


@pytest.mark.integration
def test_negative_tencim_standalone_run_file_result_not_found(session_factory):

    with pytest.raises(ResultNotFound, match="Result not found."):
        tencim_standalone_run(404)


@pytest.mark.integration
def test_negative_tencim_standalone_run_file_not_found(session_factory, case):

    with session_factory as session:
        result = TencimResult(case=case)
        session.add_all([case, result])
        session.commit()
        session.refresh(result)
        result_id = result.id

    with pytest.raises(TaskFileCaseNotFound, match="The case has no base file."):
        tencim_standalone_run(result_id)
