from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from confiacim_api.database import ActiveSession
from confiacim_api.models import User
from confiacim_api.schemas import UserCreate, UserOut
from confiacim_api.security import get_password_hash

router = APIRouter(prefix="/api", tags=["User"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(session: ActiveSession, payload: UserCreate):
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
