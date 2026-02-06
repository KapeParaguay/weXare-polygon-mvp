from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.experience_record import ExperienceRecord
from app.models.reputation_log import ReputationLog

FORMULA_VERSION = "v1"


@dataclass
class Reputation:
    user_id: str
    role: str
    score: float
    formula_version: str


def _elo_update(current: float, outcome: str) -> float:
    # Simple v1: +10 success, -10 fail, +2 split
    if outcome == "SUCCESS":
        return current + 10
    if outcome == "FAIL":
        return current - 10
    if outcome == "SPLIT":
        return current + 2
    return current


def calculate_reputation(db: Session, user_id: str, role: str) -> Reputation:
    records = db.query(ExperienceRecord).filter(
        ExperienceRecord.user_id == user_id,
        ExperienceRecord.role == role,
        ExperienceRecord.executor_type == "HUMAN",
    ).all()
    score = 1000.0
    for r in records:
        score = _elo_update(score, r.outcome)
    return Reputation(user_id=user_id, role=role, score=score, formula_version=FORMULA_VERSION)


def log_reputation_change(db: Session, user_id: str, role: str, prev: float, new: float) -> None:
    db.add(
        ReputationLog(
            user_id=user_id,
            role=role,
            previous_score=prev,
            new_score=new,
            formula_version=FORMULA_VERSION,
            created_at=datetime.utcnow(),
        )
    )
    db.commit()
