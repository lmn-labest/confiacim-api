from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, FormResult
from confiacim_api.schemes import (
    FormConfigCreate,
    FormResultDetail,
    FormResultSummary,
    ResultCeleryTask,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import form_run as form_task

router = APIRouter(prefix="/api/case", tags=["Form"])


@router.get("/{case_id}/form/results", response_model=Page[FormResultSummary])
def form_result_list(session: ActiveSession, user: CurrentUser, case_id: int):
    """Lista o resultados do **FORM** do usuário logado para o `case_id`"""

    case = session.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    stmt = (
        select(FormResult)
        .join(FormResult.case)
        .where(
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )

    return paginate(session, stmt)


@router.post("/{case_id}/form/run", response_model=ResultCeleryTask)
def form_run(
    session: ActiveSession,
    case_id: int,
    config: FormConfigCreate,
    user: CurrentUser,
):
    """Envia uma simulação do `FORM` do caso `case_id` para a fila de execução"""

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

    payload_configs = config.model_dump(exclude_unset=True)

    result = FormResult(case=case, config=payload_configs["form"], critical_point=payload_configs["critical_point"])
    session.add(result)
    session.commit()
    session.refresh(result)

    task = form_task.delay(result_id=result.id)

    return {
        "task_id": task.id,
        "result_id": result.id,
    }


@router.get(
    "/{case_id}/form/results/{result_id}",
    response_model=FormResultDetail,
)
def form_result_retrive(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    result_id: int,
):
    """Retorna o resultado do `FORM` vom `result_id` do caso `case_id` do usuário logado"""

    stmt = (
        select(FormResult)
        .join(FormResult.case)
        .where(
            FormResult.id == result_id,
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
