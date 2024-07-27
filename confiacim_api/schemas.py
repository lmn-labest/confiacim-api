from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from confiacim_api.const import MAX_TAG_NAME_LENGTH


class Health(BaseModel):
    status: str


class Message(BaseModel):
    message: str


class CaseCreate(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)


class CasePublic(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)


# class SimulationUpdate(BaseModel):
#     tag: str | None = Field(default=None, max_length=30)


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
