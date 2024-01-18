from uuid import UUID

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class SimulationCreate(BaseModel):
    tag: str = Field(max_length=30)


class SimulationPublic(BaseModel):
    id: int
    tag: str = Field(max_length=30)
    celery_task_id: UUID | None


class SimulationUpdate(BaseModel):
    tag: str | None = Field(default=None, max_length=30)


class SimulationList(BaseModel):
    simulations: list[SimulationPublic]
