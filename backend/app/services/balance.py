from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.escrow_ledger import EscrowLedger
from app.models.withdrawal import Withdrawal


@dataclass
class Balance:
    available: float
    locked: float
    pending: float


def get_balance(db: Session, user_id: str) -> Balance:
    # MVP: compute from ledger + withdrawals
    credits = sum(
        l.amount for l in db.query(EscrowLedger).filter(
            EscrowLedger.user_id == user_id,
            EscrowLedger.kind.in_(["CREDIT", "RELEASE", "REFUND", "SPLIT"]),
        ).all()
    )
    locked = sum(
        l.amount for l in db.query(EscrowLedger).filter(
            EscrowLedger.user_id == user_id,
            EscrowLedger.kind == "FUND",
        ).all()
    )
    pending = sum(
        w.amount for w in db.query(Withdrawal).filter(
            Withdrawal.user_id == user_id,
            Withdrawal.status.in_(["REQUESTED", "PROCESSING", "SENT_ONCHAIN"]),
        ).all()
    )
    available = max(0.0, credits - locked - pending)
    return Balance(available=available, locked=locked, pending=pending)
