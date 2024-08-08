from typing import Union

from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import false, select, true

from confiacim_api.database import ActiveSession
from confiacim_api.models import User
from confiacim_api.schemes import UserOut
from confiacim_api.security import CurrentUser

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=Page[UserOut])
def admin_list_users(session: ActiveSession, user: CurrentUser, role: Union[str, None] = None):
    """Rota para lista os usuarios cadastrados. Apenas usuario admins pondem acessar essa rota"""
    if user.is_admin is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
        )

    if not role:
        return paginate(session, select(User))

    if role == "admin":
        stmt = select(User).where(User.is_admin == true())
    elif role == "user":
        stmt = select(User).where(User.is_admin == false())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role filter.",
        )

    return paginate(session, stmt)
