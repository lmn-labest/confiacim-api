import pytest

from confiacim_api.models import Case
from confiacim_api.tasks import TaskFileCaseNotFound, tencim_standalone_run


@pytest.fixture
def session_factory(mocker, session):
    return mocker.patch("confiacim_api.tasks.SessionFactory", return_value=session)


@pytest.mark.slow
@pytest.mark.integration
def test_positive_tencim_standalone_run(
    case_with_real_file: Case,
    session_factory,
    mocker,
    tmp_path,
):

    mocker.patch("confiacim_api.tasks.get_simulation_base_dir", return_value=tmp_path)

    tencim_standalone_run(case_with_real_file.id)

    # TODO: Fazer o assert nos resultados


@pytest.mark.integration
def test_negative_tencim_standalone_run(session_factory):

    with pytest.raises(TaskFileCaseNotFound, match="Case files not found."):
        tencim_standalone_run(404)
