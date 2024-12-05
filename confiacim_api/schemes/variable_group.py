from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, Field, model_validator

from confiacim_api.constants import MAX_TAG_NAME_LENGTH, MIN_TAG_NAME_LENGTH
from confiacim_api.correlations import validation_correlations
from confiacim_api.errors import CorrelationsInvalidError
from confiacim_api.schemes.form import FormVariables

FORM_EXAMPLE = [
    {"name": "E_c", "dist": {"name": "lognormal", "params": {"mean": 1.0, "cov": 0.1}}},
    {"name": "poisson_c", "dist": {"name": "lognormal", "params": {"mean": 1.0, "cov": 0.1}}},
]

CORRLATIONS_EXAMPLE = [
    {"E_c, poison_c": 0.5},
]


class VariableGroupOut(BaseModel):
    id: Optional[int]

    tag: str = Field(min_length=MIN_TAG_NAME_LENGTH, max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    case_id: int = Field(serialization_alias="case")

    variables: list[FormVariables]
    correlations: Optional[dict]

    created_at: datetime
    updated_at: datetime


class VariableGroupIn(BaseModel):

    tag: str = Field(min_length=MIN_TAG_NAME_LENGTH, max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None

    variables: list[FormVariables] = Field(examples=[FORM_EXAMPLE])
    correlations: Optional[dict[str, float]] = Field(examples=[FORM_EXAMPLE], default=None)

    @model_validator(mode="after")
    def check_validation_correlations(self) -> Self:
        if self.correlations:
            variables = [{"name": v.name} for v in self.variables]
            try:
                validation_correlations(variables, self.correlations)
            except CorrelationsInvalidError as e:
                raise ValueError(str(e)) from e

        return self


class VariableGroupPatch(BaseModel):

    tag: Optional[str] = Field(min_length=MIN_TAG_NAME_LENGTH, max_length=MAX_TAG_NAME_LENGTH, default=None)
    description: Optional[str] = None

    variables: Optional[list[FormVariables]] = Field(examples=[FORM_EXAMPLE], default=None)
    correlations: Optional[dict[str, float]] = Field(examples=[FORM_EXAMPLE], default=None)
