from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from slugify import slugify
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case
from confiacim_api.schemas import (
    CaseCreate,
    CaseList,
    CasePublic,
    CeleryTask,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import tencim_standalone_run as tencim_run
from confiacim_api.utils import file_case_is_zipfile

router = APIRouter(prefix="/api/case", tags=["Case"])


@router.get("", response_model=CaseList)
def case_list(session: ActiveSession, user: CurrentUser):
    stmt = select(Case).filter(Case.user == user).order_by(Case.tag)
    cases = session.scalars(stmt).all()
    return {"cases": cases}


@router.post("", response_model=CasePublic, status_code=status.HTTP_201_CREATED)
def case_create(
    session: ActiveSession,
    payload: CaseCreate,
    user: CurrentUser,
):
    # TODO: Query lenta
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

    db_case = session.scalar(select(Case).where(Case.id == case_id, Case.user == user))

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return db_case


@router.post("/{case_id}/upload")
def upload_case_file(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
    case_file: Annotated[UploadFile, File()],
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

    if not file_case_is_zipfile(case_file.file):
        raise HTTPException(
            detail="The file must be a zip file.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    case.base_file = case_file.file.read()
    session.commit()

    return {"detail": "File upload success."}


@router.get("/{case_id}/download")
def download_case_file(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):
    """Downlaod do arquivos do `simentar`."""

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

    filename = f"{slugify(case.tag)}.zip"
    response = Response(content=case.base_file, media_type="application/zip")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response


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
