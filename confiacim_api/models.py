from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from confiacim_api.const import MAX_TAG_NAME_LENGTH


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password: Mapped[str] = mapped_column(String(1024))
    is_admin: Mapped[bool] = mapped_column(
        default=false(),
        server_default="false",
    )
    cases: Mapped[list["Case"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(email={self.email}, is_admin={self.is_admin})"


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (UniqueConstraint("tag", "user_id", name="case_tag_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(MAX_TAG_NAME_LENGTH))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="cases")
    base_file: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    tencim_results: Mapped[list["TencimResult"]] = relationship(back_populates="case")

    def __repr__(self) -> str:
        return self.tag


class TencimResult(TimestampMixin, Base):
    __tablename__ = "tencim_results"
    __table_args__ = (UniqueConstraint("task_id", "case_id", name="case_task"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[Optional[UUID]]
    istep: Mapped[Optional[tuple[int]]] = mapped_column(ARRAY(Integer, as_tuple=True))
    t: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True))
    rankine_rc: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True))
    mohr_coulomb_rc: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True))
    error: Mapped[Optional[str]] = mapped_column(Text)

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    case: Mapped["Case"] = relationship(back_populates="tencim_results")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, case={self.case})"
