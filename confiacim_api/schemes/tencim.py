from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from confiacim_api.models import ResultStatus

TArrayInt = tuple[int, ...]
TArrayFloat = tuple[float, ...]


class TencimResultSummary(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    status: Optional[ResultStatus] = None
    created_at: datetime
    updated_at: datetime


class TencimResultDetail(BaseModel):
    id: int
    task_id: Optional[UUID] = None
    istep: Optional[TArrayInt] = None
    t: Optional[TArrayFloat] = None
    rankine_rc: Optional[TArrayFloat] = None
    mohr_coulomb_rc: Optional[TArrayFloat] = None
    critical_point: Optional[PositiveInt] = None
    error: Optional[str] = None
    status: ResultStatus
    created_at: datetime
    updated_at: datetime


class TencimResultStatus(BaseModel):
    status: ResultStatus


class TencimResultError(BaseModel):
    error: Optional[str] = None


class TencimOptions(BaseModel):
    rc_limit: bool = False
    critical_point: Optional[PositiveInt] = None
