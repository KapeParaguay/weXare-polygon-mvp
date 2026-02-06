from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.task_offer import TaskOffer
from app.models.worker_profile import WorkerProfile
from app.models.user import User
from app.services.reputation import calculate_reputation
from app.services.external_sources import get_external_sources

WAVE_TIMEOUT_MIN = 30


def issue_wave(db: Session, task_id: int, count: int = 3) -> list[TaskOffer]:
    # Prioritize ACTIVE workers with higher reputation (worker role)
    workers = db.query(WorkerProfile, User).join(User, User.id == WorkerProfile.user_id).filter(User.status == "ACTIVE").limit(50).all()
    ranked = []
    for w, u in workers:
        rep = calculate_reputation(db, w.user_id, "worker")
        ranked.append((rep.score, w.user_id))
    ranked.sort(reverse=True)

    offers: list[TaskOffer] = []
    expires_at = datetime.utcnow() + timedelta(minutes=WAVE_TIMEOUT_MIN)
    for _, user_id in ranked[:count]:
        offer = TaskOffer(task_id=task_id, worker_id=user_id, status="PENDING", expires_at=expires_at)
        db.add(offer)
        offers.append(offer)
    db.commit()
    if not offers:
        # Fallback to external sources (off-chain outreach)
        _ = get_external_sources()
    return offers
