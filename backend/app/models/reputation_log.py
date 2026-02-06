from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ReputationLog(Base):
    __tablename__ = "reputation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)
    previous_score: Mapped[float] = mapped_column(Float)
    new_score: Mapped[float] = mapped_column(Float)
    formula_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
