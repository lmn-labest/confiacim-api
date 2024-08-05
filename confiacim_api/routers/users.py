from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import User
from confiacim_api.schemes import UserCreate, UserOut
from confiacim_api.security import CurrentUser, get_password_hash

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(session: ActiveSession, payload: UserCreate):
    """Cria usuário com `email` e `senha`"""
    if session.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(payload.password)

    new_user = User(email=payload.email, password=hashed_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(session: ActiveSession, user_id: int, user: CurrentUser):
    """Deleta usuário `user_id`"""

    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
        )

    session.delete(user)
    session.commit()
