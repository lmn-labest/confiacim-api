from typing import Union

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import false, select, true

from confiacim_api.database import ActiveSession
from confiacim_api.models import User
from confiacim_api.schemes import ListUsersOut
from confiacim_api.security import CurrentUser

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=ListUsersOut)
def admin_list_users(session: ActiveSession, user: CurrentUser, role: Union[str, None] = None):

    if user.is_admin is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
        )

    if not role:
        users = session.scalars(select(User).where()).all()
        return {"count": len(users), "results": users}

    if role == "admin":
        users = session.scalars(select(User).where(User.is_admin == true())).all()
    elif role == "user":
        users = session.scalars(select(User).where(User.is_admin == false())).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role filter.",
        )

    return {"count": len(users), "results": users}
