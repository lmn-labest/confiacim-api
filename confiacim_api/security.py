from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from passlib.context import CryptContext
from zoneinfo import ZoneInfo

from confiacim_api.conf import settings
from confiacim_api.database import ActiveSession
from confiacim_api.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password, hash_password) -> bool:
    return pwd_context.verify(password, hash_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: ActiveSession,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        if not id:
            raise credentials_exception
    except (DecodeError, ExpiredSignatureError) as e:
        raise credentials_exception from e

    user = session.get(User, id)

    if not user:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
