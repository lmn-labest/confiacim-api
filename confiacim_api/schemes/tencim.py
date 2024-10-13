from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from confiacim_api.models import ResultStatus

TArrayInt = tuple[int, ...]
TArrayFloat = tuple[float, ...]


class TencimResultSummaryOut(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    status: Optional[ResultStatus] = None
    created_at: datetime
    updated_at: datetime


class TencimResultDetailOut(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    istep: Optional[TArrayInt] = None
    t: Optional[TArrayFloat] = None
    rankine_rc: Optional[TArrayFloat] = None
    mohr_coulomb_rc: Optional[TArrayFloat] = None
    critical_point: Optional[PositiveInt] = None
    rc_limit: Optional[bool] = None
    description: Optional[str] = None
    error: Optional[str] = None
    status: ResultStatus
    created_at: datetime
    updated_at: datetime


class TencimResultStatusOut(BaseModel):
    status: ResultStatus


class TencimResultErrorOut(BaseModel):
    error: Optional[str] = None


class TencimCreateRunIn(BaseModel):
    rc_limit: bool = False
    critical_point: Optional[PositiveInt] = None
    description: Optional[str] = None
