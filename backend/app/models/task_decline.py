from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class TaskDecline(Base):
    __tablename__ = "task_declines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    declined_at: Mapped[DateTime] = mapped_column(DateTime)
