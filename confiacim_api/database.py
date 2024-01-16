from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from confiacim_api.conf import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.SQLALCHEMY_ECHO)


def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Annotated[Session, Depends(get_session)]
