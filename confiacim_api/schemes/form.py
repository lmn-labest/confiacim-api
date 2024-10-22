from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt

from confiacim_api.models import ResultStatus


class FormVariablesEnum(str, Enum):
    E_c = "E_c"
    poisson_c = "poisson_c"
    E_f = "E_f"
    poisson_f = "poisson_f"


class RandomDistributionEnum(str, Enum):
    normal = "normal"
    lognormal = "lognormal"
    gumbel_r = "gumbel_r"
    weibull_min = "weibull_min"
    triang = "triang"
    sgld = "sgld"
    sgld_t = "sgld_t"


class RandomDistribution(BaseModel):
    name: RandomDistributionEnum
    params: dict[str, float]


class FormVariables(BaseModel):
    name: FormVariablesEnum
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


class FormConfigCreateIn(BaseModel):
    form: FormConfig = Field(examples=[FORM_CONFIG_EXAMPLE])
    critical_point: PositiveInt
    description: Optional[str] = None


class FormResultDetailOut(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    critical_point: Optional[PositiveInt] = None
    beta: Optional[float] = None
    resid: Optional[float] = None
    it: Optional[PositiveInt] = None
    Pf: Optional[float] = None
    error: Optional[str] = None
    config: Optional[dict] = None
    variables_stats: Optional[dict] = None
    description: Optional[str] = None
    status: ResultStatus
    created_at: datetime
    updated_at: datetime


class FormResultSummaryOut(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    status: Optional[ResultStatus] = None
    created_at: datetime
    updated_at: datetime


class FormResultErrorOut(BaseModel):
    error: Optional[str] = None
