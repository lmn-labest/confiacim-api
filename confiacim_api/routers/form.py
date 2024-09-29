from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case, FormResult
from confiacim_api.schemes import (
    FormConfigCreate,
    ResultCeleryTask,
)
from confiacim_api.security import CurrentUser
from confiacim_api.tasks import form_run as form_task

router = APIRouter(prefix="/api/case", tags=["Form"])


@router.post("/{case_id}/form/run", response_model=ResultCeleryTask)
def form_run(
    session: ActiveSession,
    case_id: int,
    config: FormConfigCreate,
    user: CurrentUser,
):
    """Envia uma simulação do `form` do caso `case_id` para a fila execução"""

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

    result = FormResult(case=case, config=config.model_dump(exclude_unset=True))
    session.add(result)
    session.commit()
    session.refresh(result)

    task = form_task.delay(result_id=result.id)

    return {
        "task_id": task.id,
        "result_id": result.id,
    }
