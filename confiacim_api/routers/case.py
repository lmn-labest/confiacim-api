from dataclasses import asdict
from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from slugify import slugify
from sqlalchemy import select

from confiacim_api.constants import MAX_TAG_NAME_LENGTH, MIN_TAG_NAME_LENGTH
from confiacim_api.database import ActiveSession, Session
from confiacim_api.files_and_folders_handlers import (
    HidrationProp,
    LoadsInfos,
    MaterialsInfos,
    extract_hidration_infos_from_blob,
    extract_loads_infos_from_blob,
    extract_materials_infos_from_blob,
)
from confiacim_api.models import (
    Case,
    HidrationPropInfos,
    LoadsBaseCaseInfos,
    MaterialsBaseCaseAverageProps,
)
from confiacim_api.schemes import (
    CaseCreateIn,
    CaseCreateOut,
    CaseOut,
    HidrationPropsOut,
    LoadInfosOut,
    MaterialsOut,
)
from confiacim_api.security import CurrentUser
from confiacim_api.utils import file_case_is_zipfile

router = APIRouter(prefix="/api/case", tags=["Case"])


# TODO: Testar de forma unitaria
def _create_or_update_materials(session: Session, case: Case, mat_infos: MaterialsInfos):
    """
    Cria ou atualiza materials

    Parameters:
        session: Secção aberta com o banco
        case: Caso
        mat_infos: Informação dos materials
    """

    if case.materials is None:
        mat = MaterialsBaseCaseAverageProps(case=case, **asdict(mat_infos))
        session.add(mat)
    else:
        for k, v in asdict(mat_infos).items():
            setattr(case.materials, k, v)


# TODO: Testar de forma unitaria
def _create_or_update_loads(session: Session, case: Case, loads_infos: LoadsInfos):
    """
    Cria ou atualiza loads

    Parameters:
        session: Secção aberta com o banco
        case: Caso
        loads_infos: Informação dos carregamento
    """

    if case.loads is None:
        loads = LoadsBaseCaseInfos(
            case=case,
            nodalsource=loads_infos.nodalsource,
            mechanical_t=loads_infos.mechanical_loads.t,
            mechanical_force=loads_infos.mechanical_loads.force,
            thermal_t=loads_infos.thermal_loads.t,
            thermal_h=loads_infos.thermal_loads.h,
            thermal_temperature=loads_infos.thermal_loads.temperature,
        )
        session.add(loads)
    else:
        case.loads.nodalsource = loads_infos.nodalsource
        case.loads.mechanical_t = loads_infos.mechanical_loads.t
        case.loads.mechanical_force = loads_infos.mechanical_loads.force
        case.loads.thermal_t = loads_infos.thermal_loads.t
        case.loads.thermal_h = loads_infos.thermal_loads.h
        case.loads.thermal_temperature = loads_infos.thermal_loads.temperature


# TODO: Testar de forma unitaria
def _create_or_update_hidrationprops(session: Session, case: Case, hidration_infos: HidrationProp | None):
    """
    Cria ou atualiza hidratação

    Parameters:
        session: Secção aberta com o banco
        case: Caso
        hidration_infos: Informação da hidratação
    """

    if case.hidration_props is None:
        if hidration_infos:
            hidration = HidrationPropInfos(
                case=case,
                # E_c
                E_c_t=hidration_infos.E_c.t,
                E_c_values=hidration_infos.E_c.values,
                # poisson_c
                poisson_c_t=hidration_infos.poisson_c.t,
                poisson_c_values=hidration_infos.poisson_c.values,
                # cohesion_c
                cohesion_c_t=hidration_infos.cohesion_c.t,
                cohesion_c_values=hidration_infos.cohesion_c.values,
            )
            session.add(hidration)
    else:
        if hidration_infos:
            case.hidration_props.E_c_t = hidration_infos.E_c.t
            case.hidration_props.E_c_values = hidration_infos.E_c.values
            case.hidration_props.poisson_c_t = hidration_infos.poisson_c.t
            case.hidration_props.poisson_c_values = hidration_infos.poisson_c.values
            case.hidration_props.cohesion_c_t = hidration_infos.cohesion_c.t
            case.hidration_props.cohesion_c_values = hidration_infos.cohesion_c.values


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
    hidration_infos = extract_hidration_infos_from_blob(new_case)

    _create_or_update_materials(session, new_case, mat_infos)
    _create_or_update_loads(session, new_case, loads_infos)
    _create_or_update_hidrationprops(session, new_case, hidration_infos)

    session.commit()
    session.refresh(new_case)

    return new_case


@router.get("/{case_id}", response_model=CaseOut)
def case_retrieve(session: ActiveSession, case_id: int, user: CurrentUser):
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
    loads_infos = extract_loads_infos_from_blob(case)
    hidration_infos = extract_hidration_infos_from_blob(case)

    _create_or_update_materials(session, case, mat_infos)
    _create_or_update_loads(session, case, loads_infos)
    _create_or_update_hidrationprops(session, case, hidration_infos)

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
def material_case_retrieve(
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
def loads_case_retrieve(
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


@router.get("/{case_id}/hidration_props", response_model=HidrationPropsOut)
def hidration_props_case_retrieve(
    session: ActiveSession,
    case_id: int,
    user: CurrentUser,
):
    """Retorno a informações da propriedades de hidratação do caso `case_id`"""

    case = session.scalar(select(Case).filter(Case.id == case_id, Case.user == user))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    if not case.hidration_props:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The case not have registered hidration props",
        )

    return case.hidration_props
