from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.errors import CorrelationsInvalidError
from confiacim_api.models import (
    Case,
    VariableGroup,
)
from confiacim_api.schemes import (
    VariableGroupIn,
    VariableGroupOut,
    VariableGroupPatch,
)
from confiacim_api.security import CurrentUser
from confiacim_api.variables_group import validation_correlations

router = APIRouter(prefix="/api/case", tags=["Variable Group"])


@router.post("/{case_id}/variable_group", response_model=VariableGroupOut, status_code=status.HTTP_201_CREATED)
def variable_group_create(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    variable_group: VariableGroupIn,
):
    case = session.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    variable_group_old = session.scalar(
        select(VariableGroup).where(VariableGroup.case_id == case_id, VariableGroup.tag == variable_group.tag)
    )
    if variable_group_old:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case Tag name shoud be unique per case.",
        )

    new_variable_group = VariableGroup(
        **variable_group.model_dump(exclude_unset=True),
        case=case,
    )
    session.add(new_variable_group)
    session.commit()
    session.refresh(new_variable_group)

    return new_variable_group


@router.get("/{case_id}/variable_group/{variable_group_id}", response_model=VariableGroupOut)
def variable_group_retrieve(
    session: ActiveSession,
    case_id: int,
    variable_group_id: int,
    user: CurrentUser,
):
    """Retorno a informações do Grupo de variaveis do caso `case_id`"""

    stmt = (
        select(VariableGroup)
        .join(VariableGroup.case)
        .where(VariableGroup.id == variable_group_id, Case.id == case_id, Case.user_id == user.id)
    )

    variable_group = session.scalar(stmt)

    if not variable_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variable Group not found",
        )

    return variable_group


@router.get("/{case_id}/variable_group", response_model=Page[VariableGroupOut])
def variable_group_list(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
):
    "Lista os grupos de variaveis do usuario logado"

    case = session.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    stmt = (
        select(VariableGroup)
        .join(VariableGroup.case)
        .where(
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )

    return paginate(session, stmt)


@router.delete(
    "/{case_id}/form/variable_group/{variable_group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def variable_group_delete(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    variable_group_id: int,
):
    """Deleta o grupo de variaveis do `FORM` com `variable_group_id` do caso co `case_id` do usuário logado"""

    stmt = (
        select(VariableGroup)
        .join(VariableGroup.case)
        .where(
            VariableGroup.id == variable_group_id,
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )
    variable_group = session.scalar(stmt)

    if not variable_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variable Group/Case not found",
        )

    session.delete(variable_group)
    session.commit()


@router.patch(
    "/{case_id}/form/variable_group/{variable_group_id}",
    status_code=status.HTTP_200_OK,
    response_model=VariableGroupOut,
)
def variable_group_patch(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    variable_group_id: int,
    payload: VariableGroupPatch,
):
    """Atualiza o grupo de variaveis do `FORM` com `variable_group_id` do caso co `case_id` do usuário logado"""

    # Checa se existe outro grupo de variavel com a mesma tag
    if payload.tag and session.scalar(
        select(VariableGroup).where(
            VariableGroup.case_id == case_id,
            VariableGroup.tag == payload.tag,
            VariableGroup.id != variable_group_id,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Variable Group Tag name shoud be unique per case.",
        )

    stmt = (
        select(VariableGroup)
        .join(VariableGroup.case)
        .where(
            VariableGroup.id == variable_group_id,
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )
    variable_group_db = session.scalar(stmt)

    if not variable_group_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variable Group/Case not found",
        )

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(variable_group_db, k, v)

    if payload.correlations:
        try:
            validation_correlations([variable_group_db.variables], payload.correlations)
        except CorrelationsInvalidError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

    session.add(variable_group_db)
    session.commit()
    session.refresh(variable_group_db)

    return variable_group_db
