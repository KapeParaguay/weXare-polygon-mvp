from sqlalchemy import String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base


class WorkerProfile(Base):
    __tablename__ = "worker_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String).with_variant(JSON, "sqlite"), default=[])
    pricing: Mapped[float] = mapped_column(Float, default=0.0)
    scores: Mapped[float] = mapped_column(Float, default=0.0)
    active_task_id: Mapped[int | None] = mapped_column(default=None)
