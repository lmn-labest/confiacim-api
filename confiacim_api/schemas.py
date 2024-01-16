from pydantic import BaseModel


class SimulationPublic(BaseModel):
    id: int
    tag: str


class SimulationList(BaseModel):
    simulations: list[SimulationPublic]
