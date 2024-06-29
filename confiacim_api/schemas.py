from pydantic import BaseModel, EmailStr, Field


class Health(BaseModel):
    status: str


class Message(BaseModel):
    message: str


# class SimulationCreate(BaseModel):
#     tag: str = Field(max_length=30)


class CasePublic(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=30)
    # celery_task_id: UUID | None


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
