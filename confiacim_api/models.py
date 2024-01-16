from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Simulation(Base):
    __tablename__ = "simulation"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), unique=True)

    def __str__(self):
        return self.tag
