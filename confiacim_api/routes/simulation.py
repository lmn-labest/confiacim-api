from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from confiacim_api import celery_app
from confiacim_api.database import ActiveSession
from confiacim_api.models import Simulation
from confiacim_api.schemas import (
    Message,
    SimulationCreate,
    SimulationList,
    SimulationPublic,
    SimulationUpdate,
)
from confiacim_api.tasks import simulation_run as simulation_run_task

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get("", response_model=SimulationList)
def simulation_list(session: ActiveSession):
    query = select(Simulation)

    simulations = session.scalars(query).all()

    return {"simulations": simulations}


@router.post("", response_model=SimulationPublic, status_code=status.HTTP_201_CREATED)
def simulation_create(session: ActiveSession, payload: SimulationCreate):
    db_simulation_with_new_tag_name = session.scalar(select(Simulation).where(Simulation.tag == payload.tag))

    if db_simulation_with_new_tag_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Simulation Tag name shoud be unique.",
        )

    new_simulation = Simulation(tag=payload.tag)

    session.add(new_simulation)
    session.commit()
    session.refresh(new_simulation)

    return new_simulation


@router.get("/{simulation_id}", response_model=SimulationPublic)
def simulation_retrive(session: ActiveSession, simulation_id: int):
    query = select(Simulation).where(Simulation.id == simulation_id)

    db_simulation = session.scalar(query)

    if not db_simulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

    return db_simulation


@router.delete("/{simulation_id}")
def simulation_delete(session: ActiveSession, simulation_id: int):
    query = select(Simulation).where(Simulation.id == simulation_id)

    db_simulation = session.scalar(query)

    if not db_simulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

    session.delete(db_simulation)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{simulation_id}", response_model=SimulationPublic)
def simulation_patch(session: ActiveSession, simulation_id: int, payload: SimulationUpdate):
    db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))

    if not db_simulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

    db_simulation_with_new_tag_name = session.scalar(select(Simulation).where(Simulation.tag == payload.tag))

    if db_simulation_with_new_tag_name and db_simulation.id != db_simulation_with_new_tag_name.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Simulation Tag name shoud be unique.",
        )

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(db_simulation, k, v)

    session.add(db_simulation)
    session.commit()
    session.refresh(db_simulation)

    return db_simulation


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
