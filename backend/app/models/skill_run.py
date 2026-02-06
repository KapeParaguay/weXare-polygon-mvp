from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SkillRun(Base):
    __tablename__ = "skill_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quest_id: Mapped[int] = mapped_column(Integer, index=True)
    skill_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # success|needs_human|failed
    artifact_url: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
