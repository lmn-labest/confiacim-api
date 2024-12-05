import re

from confiacim.controllers.base import version as core_versions
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from confiacim_api import __version__
from confiacim_api.celery import celery_app
from confiacim_api.database import ActiveSession
from confiacim_api.schemes import HealthOut, Message, VersionOut
from confiacim_api.system_stats import (
    count_case_with_simulation_success,
    count_tasks,
    total_success_simulations,
)

router = APIRouter(prefix="/api", tags=["Base"])


def check_db(session: ActiveSession) -> bool:
    try:
        session.execute(text("select 1+1"))
    except OperationalError:
        return False
    return True


@router.get("/", response_model=Message)
def index():
    return {"message": "Api do confiacim"}


@router.get("/db_health_check", response_model=HealthOut)
def health(session: ActiveSession):
    """Testa a conexão com banco de dados"""
    return {"status": "ok" if check_db(session) else "fail"}


@router.get("/system_stats")
def system_stats(session: ActiveSession):
    """Retorna o status de carga do sistema"""
    inspector = celery_app.control.inspect()

    return {
        "number_of_simulations_in_queue": count_tasks(inspector.reserved()),
        "runnings_simulation": count_tasks(inspector.active()),
        "total_simulation": total_success_simulations(session),
        "total_projects_with_simulations": count_case_with_simulation_success(session),
    }


VERSION_CORE_REGEX = re.compile(r"\d{1,2}.\d{2}.\d{1,2}")


@router.get("/versions", response_model=VersionOut)
def versions():
    """Rota que retorna a versões da `api`, `core` e `tencim1D`"""
    core, tencim = re.findall(VERSION_CORE_REGEX, core_versions())
    return {
        "api": __version__,
        "core": core,
        "tencim1D": tencim,
    }
