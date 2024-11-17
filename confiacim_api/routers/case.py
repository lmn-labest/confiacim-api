from dataclasses import asdict
from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from slugify import slugify
from sqlalchemy import select

from confiacim_api.const import MAX_TAG_NAME_LENGTH, MIN_TAG_NAME_LENGTH
from confiacim_api.database import ActiveSession
from confiacim_api.files_and_folders_handlers import (
    extract_loads_infos_from_blob,
    extract_materials_infos_from_blob,
)
from confiacim_api.models import (
    Case,
    LoadsBaseCaseInfos,
    MaterialsBaseCaseAverageProps,
)
from confiacim_api.schemes import (
    CaseCreateIn,
    CaseCreateOut,
    CaseOut,
    LoadInfosOut,
    MaterialsOut,
)
from confiacim_api.security import CurrentUser
from confiacim_api.utils import file_case_is_zipfile

router = APIRouter(prefix="/api/case", tags=["Case"])


@router.get("", response_model=Page[CaseOut])
def case_list(session: ActiveSession, user: CurrentUser):
    "Lista os casos do usuario logado"
    return paginate(session, select(Case).filter(Case.user == user).order_by(Case.tag))


@router.post("", response_model=CaseCreateOut, status_code=status.HTTP_201_CREATED)
def case_create(
    session: ActiveSession,
    user: CurrentUser,
    case_file: Annotated[UploadFile, File()],
    tag: Annotated[str, Form(min_length=MIN_TAG_NAME_LENGTH, max_length=MAX_TAG_NAME_LENGTH)],
    description: Annotated[Optional[str], Form()] = None,
):
    form_data = CaseCreateIn(tag=tag, description=description)

    db_case_with_new_tag_name = session.scalar(select(Case).where(Case.tag == form_data.tag, Case.user == user))

    if db_case_with_new_tag_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case Tag name shoud be unique per user.",
        )

    if not file_case_is_zipfile(case_file.file):
        raise HTTPException(
            detail="The file must be a zip file.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    new_case = Case(**form_data.model_dump(exclude_unset=True), user=user)

    new_case.base_file = case_file.file.read()

    mat_infos = extract_materials_infos_from_blob(new_case)
    loads_infos = extract_loads_infos_from_blob(new_case)

    mat = MaterialsBaseCaseAverageProps(case=new_case, **asdict(mat_infos))
    loads = LoadsBaseCaseInfos(
        case=new_case,
        #
        nodalsource=loads_infos.nodalsource,
        #
        mechanical_istep=loads_infos.mechanical_loads.istep,
        mechanical_force=loads_infos.mechanical_loads.force,
        #
        thermal_istep=loads_infos.thermal_loads.istep,
        thermal_h=loads_infos.thermal_loads.h,
        thermal_temperature=loads_infos.thermal_loads.temperature,
    )
    session.add_all([new_case, mat, loads])
    session.commit()
    session.refresh(new_case)

    return new_case


@router.get("/{case_id}", response_model=CaseOut)
def case_retrive(session: ActiveSession, case_id: int, user: CurrentUser):
    """Retorna o caso `case_id`"""

    db_case = session.scalar(
        select(Case).where(
            Case.id == case_id,
            Case.user == user,
        )
    )

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return db_case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def case_delete(session: ActiveSession, case_id: int, user: CurrentUser):
    """Deleta o caso `case_id`. Quando um `caso` é deletado os resultado
    associados a ele são deletados também.
    """

    db_case = session.scalar(
        select(Case).where(
            Case.id == case_id,
            Case.user == user,
        )
    )

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    session.delete(db_case)
    session.commit()


@router.post("/{case_id}/upload")
def upload_case_file(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
    case_file: Annotated[UploadFile, File()],
):
    """
    Upload do arquivos do `simentar` para o caso `case_id`.
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

    mat_infos = extract_materials_infos_from_blob(case)

    # Primeiro upload
    if case.materials is None:
        mat = MaterialsBaseCaseAverageProps(case=case, **asdict(mat_infos))
        session.add(mat)
    else:
        for k, v in asdict(mat_infos).items():
            setattr(case.materials, k, v)

    session.commit()

    return {"detail": "File upload success."}


@router.get("/{case_id}/download")
def download_case_file(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):
    """Download do arquivos do `simentar` do caso `case_id`"""

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


@router.get("/{case_id}/materials", response_model=MaterialsOut)
def material_case_retrive(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):
    """Retorno a informações do materiais do caso `case_id`"""

    case = session.scalar(select(Case).filter(Case.id == case_id, Case.user == user))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    if not case.materials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The case not have registered materials",
        )

    return case.materials


@router.get("/{case_id}/loads_infos", response_model=LoadInfosOut)
def loads_case_retrive(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):
    """Retorno a informações do loads do caso `case_id`"""

    case = session.scalar(select(Case).filter(Case.id == case_id, Case.user == user))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    if not case.loads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The case not have registered loads",
        )

    return case.loads
