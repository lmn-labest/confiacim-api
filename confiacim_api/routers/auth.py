from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import User
from confiacim_api.schemes import Token, UserOut
from confiacim_api.security import (
    CurrentUser,
    create_access_token,
    verify_password,
)

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(prefix="/api/auth", tags=["Auth"])

token_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Incorrect email or password",
)


@router.post("/token", name="token", response_model=Token)
def get_access_token(session: ActiveSession, form_data: OAuth2Form):
    """Obten o `token`S de acesso"""

    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise token_exception

    if not verify_password(form_data.password, user.password):
        raise token_exception

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/whoiam", response_model=UserOut)
def whoiam(user: CurrentUser):
    """Verifica o usuario logado"""

    return user
