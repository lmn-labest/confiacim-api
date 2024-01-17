from pydantic import BaseModel, Field


class SimulationCreate(BaseModel):
    tag: str = Field(max_length=30)


class SimulationPublic(BaseModel):
    id: int
    tag: str = Field(max_length=30)


class SimulationUpdate(BaseModel):
    tag: str | None = Field(default=None, max_length=30)


class SimulationList(BaseModel):
    simulations: list[SimulationPublic]
