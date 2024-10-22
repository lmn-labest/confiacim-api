from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from confiacim_api.const import MAX_TAG_NAME_LENGTH
from confiacim_api.schemes.tencim import TencimResultSummaryOut


class MaterialsOut(BaseModel):
    id: int
    #
    E_c: float
    poisson_c: float
    thermal_expansion_c: float
    thermal_conductivity_c: float
    volumetric_heat_capacity_c: float
    friction_angle_c: float
    cohesion_c: float
    #
    poisson_f: float
    E_f: float
    thermal_expansion_f: float
    thermal_conductivity_f: float
    volumetric_heat_capacity_f: float
    #
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CaseCreateIn(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None


class CaseCreateOut(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    materials: MaterialsOut
    created_at: datetime
    updated_at: datetime


class CaseOut(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    tencim_results: list[TencimResultSummaryOut] = Field(serialization_alias="tencim_result_ids")
    created_at: datetime
    updated_at: datetime
