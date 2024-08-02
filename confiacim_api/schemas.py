from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_serializer

from confiacim_api.const import MAX_TAG_NAME_LENGTH


class Health(BaseModel):
    status: str


class Message(BaseModel):
    message: str


class CaseCreate(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)


class TencimResultId(BaseModel):
    id: int


class TencimResult(BaseModel):
    id: int
    task_id: UUID
    created_at: datetime
    updated_at: datetime


class CasePublic(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    tencim_results: list = Field(serialization_alias="tencim_result_ids")
    created_at: datetime
    updated_at: datetime

    @field_serializer("tencim_results")
    def tencim_result_ids(self, tencim_results, _info) -> list[int]:
        return [t.id for t in tencim_results]


class CaseList(BaseModel):
    cases: list[CasePublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class ListUsersOut(BaseModel):
    count: int
    results: list[UserOut]


class CeleryTask(BaseModel):
    detail: str
    task_id: UUID
