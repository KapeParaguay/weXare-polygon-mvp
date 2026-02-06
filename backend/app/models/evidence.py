from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(String, index=True)
    task_id: Mapped[int | None] = mapped_column(Integer, default=None)
    quest_id: Mapped[int | None] = mapped_column(Integer, default=None)
    url: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
