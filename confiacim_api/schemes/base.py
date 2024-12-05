from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HealthOut(BaseModel):
    status: str


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ResultCeleryTaskOut(BaseModel):
    result_id: int
    task_id: UUID


class VersionOut(BaseModel):
    api: str = Field(examples=["0.1.0"])
    core: Optional[str] = Field(examples=["0.16.0"], default=None)
    tencim1D: Optional[str] = Field(examples=["24.11.04"], default=None)
