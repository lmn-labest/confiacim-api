from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from confiacim_api.const import MAX_TAG_NAME_LENGTH
from confiacim_api.schemes.tencim import TencimResultSummaryOut


class CaseCreateIn(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None


class CaseOut(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    tencim_results: list[TencimResultSummaryOut] = Field(serialization_alias="tencim_result_ids")
    created_at: datetime
    updated_at: datetime


class MaterialsOut(BaseModel):
    id: int
    E_c: float
    E_f: float
    poisson_c: float
    poisson_f: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
