from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Simulation
from confiacim_api.schemas import SimulationList, SimulationPublic

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get("", response_model=SimulationList)
def simulation_list(session: ActiveSession):
    query = select(Simulation)

    simulations = session.scalars(query).all()

    return {"simulations": simulations}


@router.get("/{simulation_id}", response_model=SimulationPublic)
def simulation_retrive(session: ActiveSession, simulation_id: int):
    query = select(Simulation).where(Simulation.id == simulation_id)

    simulation_db = session.scalar(query)

    if not simulation_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

    return simulation_db
