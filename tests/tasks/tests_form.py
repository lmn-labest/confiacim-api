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

        assert result_from_db.beta == pytest.approx(1.0745444487743427)
        assert result_from_db.resid == pytest.approx(0.00013781849291374292)
        assert result_from_db.it == 3
        assert result_from_db.Pf == pytest.approx(0.14128936713932422)

        assert result_from_db.variables_stats is not None

        assert result_from_db.variables_stats["E_c"]["importance_factor"] == pytest.approx(24.739161756102167)
        assert result_from_db.variables_stats["E_c"]["omission_factor"] == pytest.approx(1.1526978269674566)

        assert result_from_db.variables_stats["poisson_c"]["importance_factor"] == pytest.approx(2.3769124601955625)
        assert result_from_db.variables_stats["poisson_c"]["omission_factor"] == pytest.approx(1.0121007122432817)

        assert result_from_db.variables_stats["internal_pressure"]["importance_factor"] == pytest.approx(
            72.88392578370228
        )
        assert result_from_db.variables_stats["internal_pressure"]["omission_factor"] == pytest.approx(
            1.9203774297491962
        )

        assert result_from_db.variables_stats["internal_temperature"]["importance_factor"] == pytest.approx(0.0)
        assert result_from_db.variables_stats["internal_temperature"]["omission_factor"] == pytest.approx(1.0)

        expected_values = (1.1336004085260278, 1.0746925408708417, 1.0745444487743427)
        for db, expected in zip(result_from_db.iteration_infos["beta"], expected_values):
            assert db == pytest.approx(expected)

        expected_values = (1.0, 0.05481369360529118, 0.00013781849291374292)
        for db, expected in zip(result_from_db.iteration_infos["resid"], expected_values):
            assert db == pytest.approx(expected)

        expected_values = (1.0519945182826513, 1.0495651093155107, 1.0495254852408304)
        for db, expected in zip(result_from_db.iteration_infos["E_c"], expected_values):
            assert db == pytest.approx(expected)

        expected_values = (0.9771881579989782, 0.9787658380499211, 0.9787290075346774)
        for db, expected in zip(result_from_db.iteration_infos["poisson_c"], expected_values):
            assert db == pytest.approx(expected)

        expected_values = (1.0961184932516412, 1.0903894385880526, 1.0903871605051194)
        for db, expected in zip(result_from_db.iteration_infos["internal_pressure"], expected_values):
            assert db == pytest.approx(expected)

        expected_values = (0.9950371902099893, 0.9950371902099893, 0.9950371902099893)
        for db, expected in zip(result_from_db.iteration_infos["internal_temperature"], expected_values):
            assert db == pytest.approx(expected)

        assert result_from_db.generated_case_files is not None


@pytest.mark.slow
@pytest.mark.integration
def test_positive_form_run_with_critical_point(
    form_results_with_critical_point: FormResult,
    session_factory,
    mocker,
    tmp_path,
):
    import confiacim_api.tasks

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)
    rewrite_case_file_mocker = mocker.spy(confiacim_api.tasks, "rewrite_case_file")
    form_run(form_results_with_critical_point.id)

    with session_factory as session:
        result_from_db = session.get(FormResult, form_results_with_critical_point.id)
        assert result_from_db.status == ResultStatus.SUCCESS

        assert result_from_db.beta == pytest.approx(3.3495977717461436)
        assert result_from_db.resid == pytest.approx(4.103337767469164e-06)
        assert result_from_db.it == 4
        assert result_from_db.Pf == pytest.approx(0.00040464494007775854)

        assert result_from_db.variables_stats is not None

        assert result_from_db.variables_stats["E_c"]["importance_factor"] == pytest.approx(25.01631795137409)
        assert result_from_db.variables_stats["E_c"]["omission_factor"] == pytest.approx(1.154826174529115)

        assert result_from_db.variables_stats["poisson_c"]["importance_factor"] == pytest.approx(1.9448809633433028)
        assert result_from_db.variables_stats["poisson_c"]["omission_factor"] == pytest.approx(1.0098685896580692)

        assert result_from_db.variables_stats["internal_pressure"]["importance_factor"] == pytest.approx(
            73.03880108528261
        )
        assert result_from_db.variables_stats["internal_pressure"]["omission_factor"] == pytest.approx(
            1.9258852177209818
        )

        assert result_from_db.variables_stats["internal_temperature"]["importance_factor"] == pytest.approx(0.0)
        assert result_from_db.variables_stats["internal_temperature"]["omission_factor"] == pytest.approx(1.0)

    assert "critical_point=160" in str(rewrite_case_file_mocker.call_args)


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
