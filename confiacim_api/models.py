from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password: Mapped[str] = mapped_column(String(1024))
    is_admin: Mapped[bool] = mapped_column(default=False, server_default="false")
    cases: Mapped[list["Case"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(email={self.email}, is_admin={self.is_admin})"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="cases")

    def __repr__(self) -> str:
        return self.tag


# class Simulation(Base):
#     __tablename__ = "simulation"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     tag: Mapped[str] = mapped_column(String(30), unique=True)
#     celery_task_id: Mapped[uuid.UUID] = mapped_column(types.Uuid, nullable=True, default=None)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     user: Mapped["User"] = relationship(back_populates="simulations")

#     def __repr__(self) -> str:
#         return self.tag
