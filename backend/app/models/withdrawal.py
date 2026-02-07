from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String, default="moonpay")
    destination: Mapped[str | None] = mapped_column(String, default=None)
    country: Mapped[str | None] = mapped_column(String, default=None)
    gross_usdc: Mapped[float | None] = mapped_column(Float, default=None)
    estimated_fee_usd: Mapped[float | None] = mapped_column(Float, default=None)
    estimated_net_usd: Mapped[float | None] = mapped_column(Float, default=None)
    status: Mapped[str] = mapped_column(String, default="REQUESTED")
    tx_hash: Mapped[str | None] = mapped_column(String, default=None)
    provider_session_id: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
