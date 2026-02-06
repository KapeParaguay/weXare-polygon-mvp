from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String, default="OPEN")
    quest_id: Mapped[int] = mapped_column(Integer, index=True)
    opened_by: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    evidence: Mapped[str] = mapped_column(String)
