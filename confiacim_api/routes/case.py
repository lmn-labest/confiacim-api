from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import Case
from confiacim_api.schemas import (
    CaseCreate,
    CaseList,
    CasePublic,
)
from confiacim_api.security import CurrentUser

router = APIRouter(prefix="/api/case", tags=["Case"])


@router.get("", response_model=CaseList)
def case_list(session: ActiveSession, user: CurrentUser):
    stmt = select(Case).filter(Case.user == user).order_by(Case.tag)
    cases = session.scalars(stmt).all()
    return {"cases": cases}


@router.post(
    "",
    response_model=CasePublic,
    status_code=status.HTTP_201_CREATED,
)
def case_create(
    session: ActiveSession,
    payload: CaseCreate,
    user: CurrentUser,
):
    db_case_with_new_tag_name = session.scalar(select(Case).where(Case.tag == payload.tag, Case.user == user))

    if db_case_with_new_tag_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case Tag name shoud be unique per user.",
        )

    new_case = Case(tag=payload.tag, user=user)

    session.add(new_case)
    session.commit()
    session.refresh(new_case)

    return new_case


# @router.get("/{simulation_id}", response_model=SimulationPublic)
# def simulation_retrive(session: ActiveSession, simulation_id: int):
#     db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))

#     if not db_simulation:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

#     return db_simulation


# @router.delete("/{simulation_id}")
# def simulation_delete(session: ActiveSession, simulation_id: int):
#     db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))

#     if not db_simulation:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

#     session.delete(db_simulation)
#     session.commit()

#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.patch("/{simulation_id}", response_model=SimulationPublic)
# def simulation_patch(session: ActiveSession, simulation_id: int, payload: SimulationUpdate):
#     db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))

#     if not db_simulation:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

#     db_simulation_with_new_tag_name = session.scalar(select(Simulation).where(Simulation.tag == payload.tag))

#     if db_simulation_with_new_tag_name and db_simulation.id != db_simulation_with_new_tag_name.id:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Simulation Tag name shoud be unique.",
#         )

#     for k, v in payload.model_dump(exclude_unset=True).items():
#         setattr(db_simulation, k, v)

#     session.add(db_simulation)
#     session.commit()
#     session.refresh(db_simulation)

#     return db_simulation