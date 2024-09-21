import json
from pathlib import Path

import yaml
from confiacim.controllers.form import run as run_form_core
from confiacim.controllers.tencim import run as run_tencim_core
from confiacim.erros import (
    FormStepModZeroError,
    FormStepUaInfError,
    InvalidDistributionError,
    MissingNoRcNoClip,
    PropValueMissingError,
    SimulationConfigFileError,
    TencimRunError,
    VariableTemplateError,
)
from confiacim.simulation_config import (
    JsonIndentValueError,
    RCCriteriaInvalidOptionError,
    ResultFilesInvalidOptionError,
)
from confiacim.tencim.results import read_rc_file
from confiacim.variables.weibull_params import NoConvergenceWeibullParams
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from confiacim_api.celery import celery_app
from confiacim_api.database import SessionFactory
from confiacim_api.errors import ResultNotFound, TaskFileCaseNotFound
from confiacim_api.files_and_folders_handlers import (
    clean_temporary_simulation_folder,
    extract_materials_infos,
    rewrite_case_file,
    temporary_simulation_folder,
    unzip_tencim_case,
)
from confiacim_api.generate_templates_form import generate_materials_template
from confiacim_api.logger import logger
from confiacim_api.models import FormResult, ResultStatus, TencimResult


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
        run_tencim_core(input_dir=input_base_dir, output_dir=None, verbose_level=0)

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


@celery_app.task(bind=True, ignore_result=True)
def form_run(self, result_id: int):

    task_id = self.request.id

    with SessionFactory() as session:
        stmt = (
            select(FormResult)
            .where(FormResult.id == result_id)
            .options(
                joinedload(FormResult.case),
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
    base_folder = Path(tmp_dir.name)
    unzip_tencim_case(result.case, tmp_dir)
    logger.info(f"Task {task_id} - Extract.")
    logger.info(f"Task {task_id} - Writing case file ...")
    rewrite_case_file(
        task_id=task_id,
        case_path=base_folder / "case.dat",
        setpnode_and_setptime=True,
    )
    logger.info(f"Task {task_id} - Write.")

    logger.info(f"Task {task_id} - Creating templates ...")
    materials = base_folder / "materials.dat"

    base_folder_template = base_folder / "templates"
    base_folder_template.mkdir(exist_ok=True)

    logger.info(f"Task {task_id} - Generating materials.jinja ...")
    variables_name = tuple(var["name"] for var in result.config["variables"])

    materilas_str = materials.read_text()
    mat_infos = extract_materials_infos(materilas_str)
    mat_props = {name: getattr(mat_infos, name) for name in variables_name}
    jinja_str = generate_materials_template(
        materilas_str,
        mat_props,
    )
    materials_jinja = base_folder_template / "materials.jinja"
    materials_jinja.write_text(jinja_str)

    logger.info(f"Task {task_id} - Create.")

    logger.info(f"Task {task_id} - Create case.yml ...")
    with open(base_folder / "case.yml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(result.config, yaml_file, encoding="utf-8")
    logger.info(f"Task {task_id} - Create.")

    input_base_dir = Path(tmp_dir.name)

    with SessionFactory() as session:
        result.task_id = self.request.id
        result.status = ResultStatus.RUNNING
        session.add(result)
        session.commit()
        session.refresh(result)

    try:
        logger.info(f"Task {task_id} - Running task ...")
        run_form_core(input_dir=input_base_dir, output_dir=None, verbose_level=0)

        result_form = json.load((base_folder / "output/form/results.json").open())

        result.beta = result_form["beta"]
        result.resid = result_form["resid"]
        result.it = result_form["it"]
        result.Pf = result_form["Pf"]
        result.status = ResultStatus.SUCCESS

        logger.info(f"Task {task_id} - Analysis completed.")

    except TencimRunError as e:
        logger.warning(f"Task {task_id} - Tencim error.")
        result.error = str(e)
        result.status = ResultStatus.FAILED
        raise e

    except (
        MissingNoRcNoClip,
        SimulationConfigFileError,
        JsonIndentValueError,
        FormStepModZeroError,
        FormStepUaInfError,
        NoConvergenceWeibullParams,
        ResultFilesInvalidOptionError,
        InvalidDistributionError,
        VariableTemplateError,
        PropValueMissingError,
        RCCriteriaInvalidOptionError,
    ) as e:
        logger.warning(f"Task {task_id} - Form error.")
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
