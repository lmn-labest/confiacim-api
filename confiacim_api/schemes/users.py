from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class ListUsersOut(BaseModel):
    count: int
    results: list[UserOut]
