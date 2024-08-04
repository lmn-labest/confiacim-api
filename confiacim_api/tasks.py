from pathlib import Path

from confiacim.controllers.tencim import run
from confiacim.erros import TencimRunError
from confiacim.tencim.results import read_rc_file
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from confiacim_api.celery import celery_app
from confiacim_api.database import SessionFactory
from confiacim_api.files_and_folders_handlers import (
    clean_temporary_simulation_folder,
    temporary_simulation_folder,
    unzip_tencim_case,
)
from confiacim_api.models import ResultStatus, TencimResult


class TaskFileCaseNotFound(Exception): ...


class ResultNotFound(Exception): ...


def get_simulation_base_dir(user_id: int) -> Path:
    return Path.cwd() / "simulation_tmp_dir" / f"user_{user_id}"


@celery_app.task(bind=True, ignore_result=True)
def tencim_standalone_run(self, result_id: int):

    with SessionFactory() as session:
        stmt = (
            select(TencimResult)
            .where(TencimResult.id == result_id)
            .options(
                joinedload(TencimResult.case),
            )
        )
        result = session.scalar(stmt)

    if result is None:
        raise ResultNotFound("Result not found.")

    if result.case.base_file is None:
        raise TaskFileCaseNotFound("The case has no base file.")

    base_dir = get_simulation_base_dir(result.case.user_id)

    if not base_dir.exists():
        base_dir.mkdir(parents=True)

    tmp_dir = temporary_simulation_folder(base_dir)
    unzip_tencim_case(result.case, tmp_dir)
    input_base_dir = Path(tmp_dir.name)

    with SessionFactory() as session:
        result.task_id = self.request.id
        result.status = ResultStatus.RUNNING
        session.add(result)
        session.commit()
        session.refresh(result)

    try:
        run(input_dir=input_base_dir, output_dir=None, verbose_level=0)

        result_tencim = read_rc_file(input_base_dir / "output/case_RC.txt")

        result.istep = result_tencim.istep.tolist()
        result.t = result_tencim.t.tolist()
        result.rankine_rc = result_tencim.rc_rankine.tolist()
        result.mohr_coulomb_rc = result_tencim.rc_mhor_coulomb.tolist()
        result.status = ResultStatus.SUCCESS

    except TencimRunError as e:
        result.error = str(e)
        result.status = ResultStatus.FAILED
        raise e

    finally:
        with SessionFactory() as session:
            session.add(result)
            session.commit()
            session.refresh(result)

        clean_temporary_simulation_folder(tmp_dir)
