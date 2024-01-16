from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///database.db")


def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Annotated[Session, Depends(get_session)]
