from datetime import datetime
from sqlalchemy.orm import Session
from app.models.experience_record import ExperienceRecord


def create_experience(db: Session, user_id: str, quest_id: int, role: str, outcome: str, was_disputed: bool, dispute_result: str | None, executor_type: str = "HUMAN") -> ExperienceRecord:
    record = ExperienceRecord(
        user_id=user_id,
        quest_id=quest_id,
        role=role,
        outcome=outcome,
        was_disputed=was_disputed,
        dispute_result=dispute_result,
        executor_type=executor_type,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
