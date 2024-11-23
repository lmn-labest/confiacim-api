from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from confiacim_api.constants import MAX_TAG_NAME_LENGTH, MIN_TAG_NAME_LENGTH
from confiacim_api.schemes.tencim import TencimResultSummaryOut
from confiacim_api.types import TArrayFloat


class MaterialsOut(BaseModel):
    id: Optional[int] = None
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


class MechanicalLoads(BaseModel):
    t: TArrayFloat
    force: TArrayFloat


class ThermalLoads(BaseModel):
    t: TArrayFloat
    h: TArrayFloat
    temperature: TArrayFloat


class LoadInfosOut(BaseModel):
    id: Optional[int] = None
    #
    nodalsource: float
    #
    mechanical_t: TArrayFloat
    mechanical_force: TArrayFloat
    #
    thermal_t: TArrayFloat
    thermal_h: TArrayFloat
    thermal_temperature: TArrayFloat
    #
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HidrationPropsOut(BaseModel):
    id: Optional[int] = None
    #
    E_c_t: TArrayFloat
    E_c_values: TArrayFloat
    #
    poisson_c_t: TArrayFloat
    poisson_c_values: TArrayFloat
    #
    cohesion_c_t: TArrayFloat
    cohesion_c_values: TArrayFloat
    #
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CaseCreateIn(BaseModel):
    tag: str = Field(min_length=MIN_TAG_NAME_LENGTH, max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None


class CaseCreateOut(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    materials: MaterialsOut
    loads: LoadInfosOut
    hidration_props: Optional[HidrationPropsOut] = None
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
