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
from confiacim_api.models import Case, TencimResult


class TaskFileCaseNotFound(Exception): ...


def get_simulation_base_dir(user_id: int) -> Path:
    return Path.cwd() / "simulation_tmp_dir" / f"user_{user_id}"


@celery_app.task(bind=True)
def tencim_standalone_run(self, case_id: int) -> dict:

    with SessionFactory() as session:
        stmt = select(Case).options(joinedload(Case.user)).where(Case.id == case_id)
        case = session.scalar(stmt)
        if case is None:
            raise TaskFileCaseNotFound("Case files not found.")

    base_dir = get_simulation_base_dir(case.user.id)

    if not base_dir.exists():
        base_dir.mkdir(parents=True)

    tmp_dir = temporary_simulation_folder(base_dir)
    unzip_tencim_case(case, tmp_dir)
    input_base_dir = Path(tmp_dir.name)

    try:
        run(input_dir=input_base_dir, output_dir=None, verbose_level=0)

        results = read_rc_file(input_base_dir / "output/case_RC.txt")

        new_results = TencimResult(
            case=case,
            task_id=self.request.id,
            istep=results.istep.tolist(),
            t=results.t.tolist(),
            rankine_rc=results.rc_rankine.tolist(),
            mohr_coulomb_rc=results.rc_mhor_coulomb.tolist(),
        )

    except TencimRunError as e:
        new_results = TencimResult(
            case=case,
            task_id=self.request.id,
            error=str(e),
        )
        raise e

    finally:
        with SessionFactory() as session:
            session.add(new_results)
            session.commit()
            session.refresh(new_results)

        clean_temporary_simulation_folder(tmp_dir)

    msg = {"results_id": new_results.id}

    return msg
