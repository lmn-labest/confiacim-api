from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr


class UserCreateIn(BaseModel):
    email: EmailStr
    password: str
