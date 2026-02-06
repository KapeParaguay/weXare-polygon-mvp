from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class JudgeOffer(Base):
    __tablename__ = "judge_offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dispute_id: Mapped[int] = mapped_column(Integer, index=True)
    judge_user_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    expires_at: Mapped[DateTime] = mapped_column(DateTime)
    accepted_at: Mapped[DateTime | None] = mapped_column(DateTime, default=None)
