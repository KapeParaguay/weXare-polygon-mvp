from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class JudgeVote(Base):
    __tablename__ = "judge_votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dispute_id: Mapped[int] = mapped_column(Integer, index=True)
    judge_user_id: Mapped[str] = mapped_column(String, index=True)
    vote: Mapped[str] = mapped_column(String)
    split: Mapped[int] = mapped_column(Integer, default=0)
    comment: Mapped[str] = mapped_column(String)
