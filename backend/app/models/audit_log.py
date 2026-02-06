from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    details: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
