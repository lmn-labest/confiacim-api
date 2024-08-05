from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from confiacim_api.models import ResultStatus

TArrayInt = tuple[int, ...]
TArrayFloat = tuple[float, ...]


class TencimResultSummary(BaseModel):
    id: int
    task_id: Optional[UUID]
    status: Optional[ResultStatus]
    created_at: datetime
    updated_at: datetime


class TencimResultDetail(BaseModel):
    id: int
    task_id: Optional[UUID]
    istep: Optional[TArrayInt]
    t: Optional[TArrayFloat]
    rankine_rc: Optional[TArrayFloat]
    mohr_coulomb_rc: Optional[TArrayFloat]
    error: Optional[str]
    status: ResultStatus
    created_at: datetime
    updated_at: datetime


class ListTencimResult(BaseModel):
    results: list[TencimResultSummary]


class TencimResultStatus(BaseModel):
    status: ResultStatus


class TencimResultError(BaseModel):
    error: Optional[str]
