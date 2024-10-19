from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from confiacim_api.database import ActiveSession
from confiacim_api.schemes import HealthOut, Message

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
