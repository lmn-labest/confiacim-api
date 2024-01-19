from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api import celery_app
from confiacim_api.database import ActiveSession
from confiacim_api.models import Simulation
from confiacim_api.schemas import Message
from confiacim_api.tasks import simulation_run as simulation_run_task

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get("/{simulation_id}/run", response_model=Message, tags=["celery"], status_code=status.HTTP_202_ACCEPTED)
def simulation_run(session: ActiveSession, simulation_id: int):
    db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))

    if not db_simulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

    AsyncResult = simulation_run_task.delay(simulation_id=simulation_id)

    db_simulation.celery_task_id = AsyncResult.id
    session.add(db_simulation)
    session.commit()

    return {"message": f"A task '{AsyncResult.id}' da simulação '{db_simulation.tag}' foi mandada para a fila."}


@router.get("/celery/{task_id}/status", tags=["celery"])
def celery_task_status(task_id: UUID):
    res = AsyncResult(str(task_id), app=celery_app)

    return {"status": res.status}
