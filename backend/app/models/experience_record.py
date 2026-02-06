from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ExperienceRecord(Base):
    __tablename__ = "experience_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    quest_id: Mapped[int] = mapped_column(Integer, index=True)
    role: Mapped[str] = mapped_column(String)  # worker/judge/creator
    outcome: Mapped[str] = mapped_column(String)  # SUCCESS/FAIL/SPLIT
    was_disputed: Mapped[bool] = mapped_column(Boolean, default=False)
    dispute_result: Mapped[str | None] = mapped_column(String, default=None)
    executor_type: Mapped[str] = mapped_column(String, default="HUMAN")
    created_at: Mapped[DateTime] = mapped_column(DateTime)
