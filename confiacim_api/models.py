import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum,
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
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from confiacim_api.const import MAX_TAG_NAME_LENGTH


class ResultStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "runnig"
    FAILED = "failed"
    SUCCESS = "success"


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
    cases: Mapped[list["Case"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(email={self.email}, is_admin={self.is_admin})"


class Case(TimestampMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (UniqueConstraint("tag", "user_id", name="case_tag_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(MAX_TAG_NAME_LENGTH))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="cases")
    base_file: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    tencim_results: Mapped[list["TencimResult"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    form_results: Mapped[list["FormResult"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    materials: Mapped["MaterialsBaseCaseAverageProps"] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, case={self.tag})"


class TencimResult(TimestampMixin, Base):
    __tablename__ = "tencim_results"
    __table_args__ = (UniqueConstraint("task_id", "case_id", name="case_task_tencim_result"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[Optional[UUID]]
    istep: Mapped[Optional[tuple[int]]] = mapped_column(ARRAY(Integer, as_tuple=True), deferred=True)
    t: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True), deferred=True)
    rankine_rc: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True), deferred=True)
    mohr_coulomb_rc: Mapped[Optional[tuple[float]]] = mapped_column(ARRAY(Float, as_tuple=True), deferred=True)
    error: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[ResultStatus]] = mapped_column(
        Enum(ResultStatus, name="result_status"),
        default=ResultStatus.CREATED,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    rc_limit: Mapped[Optional[bool]]
    critical_point: Mapped[Optional[int]]

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    case: Mapped["Case"] = relationship(back_populates="tencim_results")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, case={self.case.tag})"


class FormResult(TimestampMixin, Base):
    __tablename__ = "form_results"
    __table_args__ = (UniqueConstraint("task_id", "case_id", name="case_task_form_result"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[Optional[UUID]]

    critical_point: Mapped[Optional[int]]

    beta: Mapped[Optional[float]]
    resid: Mapped[Optional[float]]
    it: Mapped[Optional[int]]
    Pf: Mapped[Optional[float]]

    error: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[ResultStatus]] = mapped_column(
        Enum(ResultStatus, name="result_status"),
        default=ResultStatus.CREATED,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    config: Mapped[dict] = mapped_column(JSON, nullable=True)
    variables_stats: Mapped[dict] = mapped_column(JSON, nullable=True)

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    case: Mapped["Case"] = relationship(back_populates="form_results")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, case={self.case.tag})"


class MaterialsBaseCaseAverageProps(TimestampMixin, Base):
    __tablename__ = "materials_base_case_average_prop"
    __table_args__ = (UniqueConstraint("case_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    E_c: Mapped[float]
    E_f: Mapped[float]
    poisson_c: Mapped[float]
    poisson_f: Mapped[float]

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    case: Mapped["Case"] = relationship(back_populates="materials")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, case={self.case.tag}, E_c={self.E_c}, ...)"
