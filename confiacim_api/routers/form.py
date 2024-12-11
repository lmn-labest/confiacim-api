from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from slugify import slugify
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, FormResult
from confiacim_api.schemes import (
    FormConfigCreateIn,
    FormResultDetailOut,
    FormResultErrorOut,
    FormResultStatusOut,
    FormResultSummaryOut,
    ResultCeleryTaskOut,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import form_run as form_task

router = APIRouter(prefix="/api/case", tags=["Form"])


@router.get("/{case_id}/form/results", response_model=Page[FormResultSummaryOut])
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


@router.post("/{case_id}/form/run", response_model=ResultCeleryTaskOut)
def form_run(
    session: ActiveSession,
    case_id: int,
    config: FormConfigCreateIn,
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

    payload_configs = config.model_dump()

    result = FormResult(
        case=case,
        config=payload_configs["form"],
        critical_point=payload_configs["critical_point"],
        description=payload_configs["description"],
    )
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
    response_model=FormResultDetailOut,
)
def form_result_retrieve(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    result_id: int,
):
    """Retorna o resultado do `FORM` com `result_id` do caso `case_id` do usuário logado"""

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


@router.delete(
    "/{case_id}/form/results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def form_result_delete(
    session: ActiveSession,
    user: CurrentUser,
    case_id: int,
    result_id: int,
):
    """Deleta o resultado do `FORM` com `result_id` do caso co `case_id` do usuário logado"""

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

    session.delete(result)
    session.commit()


@router.get("/{case_id}/form/results/{result_id}/error", response_model=FormResultErrorOut)
def form_result_error_retrieve(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Retorna o error do resultado do `FORM`."""

    result = session.scalar(
        select(FormResult)
        .join(FormResult.case)
        .where(
            FormResult.id == result_id,
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


@router.get("/{case_id}/form/results/{result_id}/status", response_model=FormResultStatusOut)
def form_result_status_retrieve(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Retorna o status do resultado do `FORM`.

    As possibiliades são:

    - CREATED - Resultdo Criando, mas a task ainda não foi enviada.
    - RUNNING - Task enviada para o broker
    - FAILED - Task falhou
    - SUCCESS - Task rodou com sucesso.

    """

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

    return {"status": result.status}


@router.get("/{case_id}/form/results/{result_id}/download-generated-case-file")
def download_form_generated_case_file(
    session: ActiveSession,
    case_id: int,
    result_id: int,
    user: CurrentUser,
):
    """Download do arquivos gerados para rodar o `confiacim` do `case_id` do resultado `result_id`"""

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
            detail="Result/Case not found.",
        )

    if result.generated_case_files is None:
        raise HTTPException(
            detail="The form result has no generated case file.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    filename = f"{slugify(result.case.tag)}.zip"
    response = Response(content=result.generated_case_files, media_type="application/zip")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response
