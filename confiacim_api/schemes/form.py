from pydantic import BaseModel, Field


class RandomDistribution(BaseModel):
    name: str
    params: dict[str, float]


class FormVariables(BaseModel):
    name: str
    dist: RandomDistribution


class FormConfigCreate(BaseModel):
    variables: list[FormVariables] = Field(min_length=1)
