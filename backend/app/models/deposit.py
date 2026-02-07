from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    amount_usd: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="INITIATED")
    provider: Mapped[str] = mapped_column(String, default="MOONPAY")
    provider_session_id: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
