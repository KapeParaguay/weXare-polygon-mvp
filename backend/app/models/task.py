from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quest_id: Mapped[int] = mapped_column(Integer, index=True)
    type: Mapped[str] = mapped_column(String)  # AI or HUMAN
    status: Mapped[str] = mapped_column(String, default="OPEN")
    assigned_user_id: Mapped[str | None] = mapped_column(String, default=None)
