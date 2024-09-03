from pathlib import Path

from confiacim.controllers.tencim import run
from confiacim.erros import TencimRunError
from confiacim.tencim.results import read_rc_file
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from confiacim_api.celery import celery_app
from confiacim_api.database import SessionFactory
from confiacim_api.errors import ResultNotFound, TaskFileCaseNotFound
from confiacim_api.files_and_folders_handlers import (
    clean_temporary_simulation_folder,
    rewrite_case_file,
    temporary_simulation_folder,
    unzip_tencim_case,
)
from confiacim_api.logger import logger
from confiacim_api.models import ResultStatus, TencimResult


def get_simulation_base_dir(user_id: int) -> Path:
    return Path.cwd() / "simulation_tmp_dir" / f"user_{user_id}"


@celery_app.task(bind=True, ignore_result=True)
def tencim_standalone_run(self, result_id: int, **options):

    task_id = self.request.id

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

    logger.info(f"Task {task_id} - Extracting case files ...")
    tmp_dir = temporary_simulation_folder(base_dir)
    unzip_tencim_case(result.case, tmp_dir)
    logger.info(f"Task {task_id} - Extract.")
    logger.info(f"Task {task_id} - Writing case file ...")
    rewrite_case_file(task_id=task_id, case_path=Path(tmp_dir.name) / "case.dat", **options)
    logger.info(f"Task {task_id} - Write.")

    input_base_dir = Path(tmp_dir.name)

    with SessionFactory() as session:
        result.task_id = self.request.id
        result.status = ResultStatus.RUNNING
        session.add(result)
        session.commit()
        session.refresh(result)

    try:
        logger.info(f"Task {task_id} - Running task ...")
        run(input_dir=input_base_dir, output_dir=None, verbose_level=0)

        result_tencim = read_rc_file(input_base_dir / "output/case_RC.txt")

        result.istep = result_tencim.istep.tolist()
        result.t = result_tencim.t.tolist()
        result.rankine_rc = result_tencim.rc_rankine.tolist()
        result.mohr_coulomb_rc = result_tencim.rc_mhor_coulomb.tolist()
        result.status = ResultStatus.SUCCESS
        logger.info(f"Task {task_id} - Analysis completed.")

    except TencimRunError as e:
        logger.warning(f"Task {task_id} - Tencim error.")
        result.error = str(e)
        result.status = ResultStatus.FAILED
        raise e

    finally:
        with SessionFactory() as session:
            session.add(result)
            session.commit()
            session.refresh(result)

        logger.debug(f"Task {task_id} - Cleaning up the temporary directory...")
        clean_temporary_simulation_folder(tmp_dir)
        logger.debug(f"Task {task_id} - Cleaned temporary directory.")
