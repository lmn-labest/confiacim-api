from uuid import UUID

from pydantic import BaseModel


class Health(BaseModel):
    status: str


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ResultCeleryTask(BaseModel):
    result_id: int
    task_id: UUID
