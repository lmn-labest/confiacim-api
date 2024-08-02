from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, TencimResult
from confiacim_api.schemas import (
    ListTencimResult,
)
from confiacim_api.security import CurrentUser

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
