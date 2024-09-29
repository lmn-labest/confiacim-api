from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from slugify import slugify
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, TencimResult
from confiacim_api.schemes import (
    ResultCeleryTask,
    TencimResultDetail,
    TencimResultStatus,
)
from confiacim_api.schemes.tencim import (  # TODO: Importar o __init__
    TencimOptions,
    TencimResultError,
    TencimResultSummary,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import tencim_standalone_run as tencim_run
from confiacim_api.write_csv import write_rc_result_to_csv

router = APIRouter(prefix="/api/case", tags=["Tencim"])


@router.get("/{case_id}/tencim/results", response_model=Page[TencimResultSummary])
def tencim_result_list(session: ActiveSession, user: CurrentUser, case_id: int):
    """Lista o resultados do usuário logado para o `case_id`"""

    case = session.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    stmt = (
        select(TencimResult)
        .join(TencimResult.case)
        .where(
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )

    return paginate(session, stmt)


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
    """Retorna o resultado `result_id` do caso `case_id` do usuário logado"""

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


@router.delete(
    "/{case_id}/tencim/results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def tencim_result_delete(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    result_id: int,
):
    """Deleta o resultado `result_id` do caso `case_id` do usuário logado"""

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

    session.delete(result)
    session.commit()


@router.post("/{case_id}/tencim/run", response_model=ResultCeleryTask)
def tencim_standalone_run(
    session: ActiveSession,
    case_id: int,
    options: TencimOptions,
    user: CurrentUser,
):
    """Envia uma simulação do `tencim` do caso `case_id` para a fila execução"""

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

    result = TencimResult(case=case)
    session.add(result)
    session.commit()
    session.refresh(result)

    task = tencim_run.delay(result_id=result.id, **options.model_dump(exclude_unset=True))

    return {
        "task_id": task.id,
        "result_id": result.id,
    }


@router.get("/{case_id}/tencim/results/{result_id}/status", response_model=TencimResultStatus)
def tencim_result_status_retrive(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Retorna o status do resultado do `tencim`.

    As possibiliades são:

    - CREATED - Resultdo Criando, mas a task ainda não foi enviada.
    - RUNNING - Task enviada para o broker
    - FAILED - Task falhou
    - SUCCESS - Task rodou com sucesso.

    """

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

    return {"status": result.status}


@router.get("/{case_id}/tencim/results/{result_id}/error", response_model=TencimResultError)
def tencim_result_error_retrive(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Retorna o error do resultado do `tencim`."""

    result = session.scalar(
        select(TencimResult)
        .join(TencimResult.case)
        .where(
            TencimResult.id == result_id,
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result/Case not found",
        )

    return {"error": result.error}


@router.get("/{case_id}/tencim/results/{result_id}/csv")
def tencim_result_retrive_csv(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Retorna download do resultados do Tencim no  formato `CSV`."""

    result = session.scalar(
        select(TencimResult)
        .join(TencimResult.case)
        .where(
            TencimResult.id == result_id,
            Case.id == case_id,
            Case.user_id == user.id,
        )
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result/Case not found",
        )

    csv_file = write_rc_result_to_csv(result)

    filename = f"{slugify(result.case.tag)}.csv"
    response = Response(content=csv_file.read(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment;filename={filename}"

    return response
