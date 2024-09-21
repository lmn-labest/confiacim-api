import pytest
from confiacim.erros import FormStepUaInfError, TencimRunError

from confiacim_api.models import (
    Case,
    FormResult,
    ResultStatus,
    User,
)
from confiacim_api.tasks import (
    ResultNotFound,
    TaskFileCaseNotFound,
    form_run,
)


@pytest.fixture
def session_factory(mocker, session):
    mocker.patch("confiacim_api.tasks.SessionFactory", return_value=session)
    return session


@pytest.fixture
def form_results_tencim_fail(
    session,
    user: User,
    form_case_config: dict,
):
    with open("tests/fixtures/case_fail.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())

    result = FormResult(
        case=case,
        config=form_case_config,
    )
    session.add_all([case, result])
    session.commit()
    session.refresh(result)

    return result


@pytest.mark.slow
@pytest.mark.integration
def test_positive_form_run(
    form_results: FormResult,
    session_factory,
    mocker,
    tmp_path,
):

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)

    form_run(form_results.id)

    with session_factory as session:
        result_from_db = session.get(FormResult, form_results.id)
        assert result_from_db.status == ResultStatus.SUCCESS
        assert result_from_db.beta is not None
        assert result_from_db.resid is not None
        assert result_from_db.it is not None
        assert result_from_db.Pf is not None


@pytest.mark.slow
@pytest.mark.integration
def test_negative_form_run_file_not_found(session_factory, case: Case):

    with session_factory as session:
        result = FormResult(case=case)
        session.add(result)
        session.commit()
        session.refresh(result)
        result_id = result.id

    with pytest.raises(TaskFileCaseNotFound, match="The case has no base file."):
        form_run(result_id)


@pytest.mark.integration
def test_negative_form_run_file_result_not_found(session_factory):

    with pytest.raises(ResultNotFound, match="Result not found."):
        form_run(404)


@pytest.mark.integration
def test_negative_form_run_tencim_error(
    form_results_tencim_fail: Case,
    session_factory,
    mocker,
    tmp_path,
):

    result_id = form_results_tencim_fail.id
    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)

    with pytest.raises(TencimRunError):
        form_run(form_results_tencim_fail.id)

    with session_factory as session:
        result_from_db = session.get(FormResult, result_id)

    assert "ERROR STOP 1" in result_from_db.error
    assert result_from_db.status == ResultStatus.FAILED


@pytest.mark.integration
def test_negative_form_run_error(
    form_results: FormResult,
    session_factory,
    mocker,
    tmp_path,
):
    """
    O confiacim pode levantar varias exceções diferentes. Aqui vamos testar apenas uma
    pois só queremos verificar se ela foi capturada e salva no DB
    """

    result_id = form_results.id
    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)
    mocker.patch("confiacim_api.tasks.run_form_core", side_effect=FormStepUaInfError)

    with pytest.raises(FormStepUaInfError):
        form_run(result_id)

    with session_factory as session:
        result_from_db = session.get(FormResult, result_id)

    assert "O vetor Ua_new tem valores infinitos." in result_from_db.error
    assert result_from_db.status == ResultStatus.FAILED
