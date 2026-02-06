from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.judge_offer import JudgeOffer
from app.models.judge_profile import JudgeProfile

ACCEPT_WINDOW_MINUTES = 30
VOTE_SLA_HOURS = 24


def create_judge_offers_wave(db: Session, dispute_id: int, count: int = 3) -> list[JudgeOffer]:
    # Only ACTIVE users should be eligible (handled by backend)
    judges = db.query(JudgeProfile).limit(count).all()
    offers: list[JudgeOffer] = []
    expires_at = datetime.utcnow() + timedelta(minutes=ACCEPT_WINDOW_MINUTES)
    for j in judges:
        offer = JudgeOffer(dispute_id=dispute_id, judge_user_id=j.user_id, status="PENDING", expires_at=expires_at)
        db.add(offer)
        offers.append(offer)
    db.commit()
    return offers


def ensure_three_judges(db: Session, dispute_id: int) -> None:
    accepted = db.query(JudgeOffer).filter(JudgeOffer.dispute_id == dispute_id, JudgeOffer.status == "ACCEPTED").count()
    pending = db.query(JudgeOffer).filter(JudgeOffer.dispute_id == dispute_id, JudgeOffer.status == "PENDING").all()
    now = datetime.utcnow()
    if accepted >= 3:
        return
    expired_pending = [o for o in pending if o.expires_at and o.expires_at < now]
    if pending and len(expired_pending) == len(pending):
        create_judge_offers_wave(db, dispute_id, count=3)


def mark_acceptance(db: Session, user_id: str, accepted: bool) -> None:
    profile = db.query(JudgeProfile).filter(JudgeProfile.user_id == user_id).first()
    if not profile:
        return
    # MVP: naive adjustment
    if accepted:
        profile.acceptance_rate = min(1.0, profile.acceptance_rate + 0.05)
    else:
        profile.acceptance_rate = max(0.0, profile.acceptance_rate - 0.05)
    db.add(profile)
    db.commit()


def flag_sla_missed(db: Session, dispute_id: int) -> None:
    now = datetime.utcnow()
    offers = db.query(JudgeOffer).filter(JudgeOffer.dispute_id == dispute_id, JudgeOffer.status == "ACCEPTED").all()
    for offer in offers:
        if offer.accepted_at and offer.accepted_at + timedelta(hours=VOTE_SLA_HOURS) < now:
            profile = db.query(JudgeProfile).filter(JudgeProfile.user_id == offer.judge_user_id).first()
            if profile:
                profile.judge_score = max(0.0, profile.judge_score - 0.1)
                db.add(profile)
    db.commit()
