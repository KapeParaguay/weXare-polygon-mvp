from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class JudgeProfile(Base):
    __tablename__ = "judge_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    judge_score: Mapped[float] = mapped_column(Float, default=0.0)
    acceptance_rate: Mapped[float] = mapped_column(Float, default=0.0)
    cooldown: Mapped[int] = mapped_column(Integer, default=0)
