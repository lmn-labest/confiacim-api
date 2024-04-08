import uuid

from sqlalchemy import String, types
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Simulation(Base):
    __tablename__ = "simulation"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), unique=True)
    celery_task_id: Mapped[uuid.UUID] = mapped_column(types.Uuid, nullable=True, default=None)

    def __str__(self):
        return self.tag
