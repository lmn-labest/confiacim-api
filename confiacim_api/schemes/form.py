from pydantic import BaseModel, Field, PositiveInt


class RandomDistribution(BaseModel):
    name: str
    params: dict[str, float]


class FormVariables(BaseModel):
    name: str
    dist: RandomDistribution


class FormConfig(BaseModel):
    variables: list[FormVariables] = Field(min_length=1)


class FormConfigCreate(BaseModel):
    form: FormConfig
    critical_point: PositiveInt
