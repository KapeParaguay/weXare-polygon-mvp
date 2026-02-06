from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class EscrowLedger(Base):
    __tablename__ = "escrow_ledger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quest_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    kind: Mapped[str] = mapped_column(String)
    onchain_tx: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
