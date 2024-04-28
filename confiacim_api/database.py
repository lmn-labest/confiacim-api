from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from confiacim_api.conf import settings
from confiacim_api.connection_string import postgresql_connection_url

database_url = postgresql_connection_url(
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    db_name=settings.DB_NAME,
    port=settings.DB_PORT,
)

engine = create_engine(database_url, echo=settings.SQLALCHEMY_ECHO)

SessionFactory = sessionmaker(engine)


def get_session():
    with SessionFactory() as session:
        yield session


ActiveSession = Annotated[Session, Depends(get_session)]
