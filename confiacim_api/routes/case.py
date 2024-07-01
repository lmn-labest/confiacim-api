import zipfile
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case
from confiacim_api.schemas import (
    CaseCreate,
    CaseList,
    CasePublic,
)
from confiacim_api.security import CurrentUser

router = APIRouter(prefix="/api/case", tags=["Case"])


@router.get("", response_model=CaseList)
def case_list(session: ActiveSession, user: CurrentUser):
    stmt = select(Case).filter(Case.user == user).order_by(Case.tag)
    cases = session.scalars(stmt).all()
    return {"cases": cases}


@router.post(
    "",
    response_model=CasePublic,
    status_code=status.HTTP_201_CREATED,
)
def case_create(
    session: ActiveSession,
    payload: CaseCreate,
    user: CurrentUser,
):
    db_case_with_new_tag_name = session.scalar(select(Case).where(Case.tag == payload.tag, Case.user == user))

    if db_case_with_new_tag_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case Tag name shoud be unique per user.",
        )

    new_case = Case(tag=payload.tag, user=user)

    session.add(new_case)
    session.commit()
    session.refresh(new_case)

    return new_case


@router.get("/{case_id}", response_model=CasePublic)
def case_retrive(session: ActiveSession, case_id: int, user: CurrentUser):

    db_simulation = session.scalar(select(Case).where(Case.id == case_id, Case.user == user))

    if not db_simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return db_simulation


@router.post("/{case_id}/upload")
def upload_case_file(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
):
    """
    Upload do arquivos do `simentar`.
    O arquivo precisa estar campactado no formato `zip`.
    """
    case = session.scalar(select(Case).filter(Case.id == case_id, Case.user == user))
    if case is None:
        raise HTTPException(
            detail="Case not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if not zipfile.is_zipfile(file.file):
        raise HTTPException(
            detail="The file must be a zip file.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return {"detail": "File upload success."}
