from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, TencimResult
from confiacim_api.schemas import (
    CeleryTask,
    ListTencimResult,
    TencimResultDetail,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import tencim_standalone_run as tencim_run

router = APIRouter(prefix="/api/case", tags=["Tencim"])


@router.get("/{case_id}/tencim/results", response_model=ListTencimResult)
def tencim_result_list(session: ActiveSession, user: CurrentUser, case_id: int):

    stmt = (
        select(TencimResult)
        .join(TencimResult.case)
        .where(
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )
    results = session.scalars(stmt).all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return {"results": results}


@router.get(
    "/{case_id}/tencim/results/{result_id}",
    response_model=TencimResultDetail,
)
def tencim_result_retrive(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    result_id: int,
):

    stmt = (
        select(TencimResult)
        .join(TencimResult.case)
        .where(
            TencimResult.id == result_id,
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )
    result = session.scalar(stmt)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result/Case not found",
        )

    return result


@router.post("/{case_id}/tencim/run", response_model=CeleryTask)
def tencim_standalone_run(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):

    case = session.scalar(select(Case).filter(Case.id == case_id, Case.user == user))

    if case is None:
        raise HTTPException(
            detail="Case not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if case.base_file is None:
        raise HTTPException(
            detail="The case has no base file.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    task = tencim_run.apply_async(args=(case_id,))

    return {"detail": "Simulation sent to queue.", "task_id": task.id}
