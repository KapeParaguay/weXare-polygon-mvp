from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    parent_quest_id: Mapped[int | None] = mapped_column(Integer, default=None)
    index: Mapped[int] = mapped_column(Integer)
    scope_hash: Mapped[str] = mapped_column(String)
    budget: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    funded_at: Mapped[DateTime | None] = mapped_column(DateTime, default=None)
