from pydantic import BaseModel, Field, PositiveInt


class RandomDistribution(BaseModel):
    name: str
    params: dict[str, float]


class FormVariables(BaseModel):
    name: str
    dist: RandomDistribution


class FormConfig(BaseModel):
    variables: list[FormVariables] = Field(min_length=1)


FORM_CONFIG_EXAMPLE = {
    "form": {
        "variables": [
            {"name": "E_c", "dist": {"name": "lognormal", "params": {"mean": 1.0, "cov": 0.1}}},
        ],
    },
}


class FormConfigCreate(BaseModel):
    form: FormConfig = Field(examples=[FORM_CONFIG_EXAMPLE])
    critical_point: PositiveInt
