"""Custodial + on-chain ledger mirror (MVP)."""
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.escrow_ledger import EscrowLedger


@dataclass
class LedgerEntry:
    quest_id: int
    user_id: str
    amount: float
    kind: str
    status: str
    tx_hash: str | None = None


def _record(db: Session, quest_id: int, user_id: str, amount: float, kind: str, status: str, tx_hash: str | None = None) -> LedgerEntry:
    entry = EscrowLedger(
        quest_id=quest_id,
        user_id=user_id,
        kind=kind,
        onchain_tx=tx_hash or "",
        amount=amount,
        status=status,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    return LedgerEntry(quest_id=quest_id, user_id=user_id, amount=amount, kind=kind, status=status, tx_hash=tx_hash)


def record_credit(db: Session, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=0, user_id=user_id, amount=amount, kind="CREDIT", status="AVAILABLE", tx_hash=tx_hash)


def record_fund(db: Session, quest_id: int, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=quest_id, user_id=user_id, amount=amount, kind="FUND", status="LOCKED", tx_hash=tx_hash)


def record_release(db: Session, quest_id: int, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=quest_id, user_id=user_id, amount=amount, kind="RELEASE", status="AVAILABLE", tx_hash=tx_hash)


def record_refund(db: Session, quest_id: int, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=quest_id, user_id=user_id, amount=amount, kind="REFUND", status="AVAILABLE", tx_hash=tx_hash)


def record_split(db: Session, quest_id: int, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=quest_id, user_id=user_id, amount=amount, kind="SPLIT", status="AVAILABLE", tx_hash=tx_hash)


def record_fee(db: Session, quest_id: int, user_id: str, amount: float, tx_hash: str | None = None) -> LedgerEntry:
    return _record(db, quest_id=quest_id, user_id=user_id, amount=amount, kind="FEE", status="AVAILABLE", tx_hash=tx_hash)
