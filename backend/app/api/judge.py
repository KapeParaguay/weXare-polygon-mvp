from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.judge_offer import JudgeOffer
from app.models.dispute import Dispute
from app.models.judge_vote import JudgeVote
from app.models.audit_log import AuditLog
from app.models.quest import Quest
from app.schemas.judge import JudgeDecision, JudgeVoteIn
from app.services.auth import get_current_user
from app.services.judges import ensure_three_judges, mark_acceptance, flag_sla_missed
from app.services.privy import sign_and_send_tx
from app.services.ledger import record_release, record_refund, record_split

router = APIRouter()


@router.get("/judge/offers")
def judge_offers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    offers = db.query(JudgeOffer).filter(JudgeOffer.judge_user_id == user["id"]).all()
    return {"offers": offers}


@router.post("/judge/offers/{offer_id}/accept")
def accept_offer(offer_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    offer = db.get(JudgeOffer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.expires_at and offer.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Offer expired")
    offer.status = "ACCEPTED"
    offer.accepted_at = datetime.utcnow()
    db.add(offer)
    mark_acceptance(db, user["id"], True)
    db.add(AuditLog(actor_id=user["id"], action="JUDGE_ACCEPT", details=str(offer_id), created_at=datetime.utcnow()))
    db.commit()
    ensure_three_judges(db, offer.dispute_id)
    return {"status": "ok"}


@router.post("/judge/offers/{offer_id}/decline")
def decline_offer(offer_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    offer = db.get(JudgeOffer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer.status = "DECLINED"
    db.add(offer)
    mark_acceptance(db, user["id"], False)
    db.add(AuditLog(actor_id=user["id"], action="JUDGE_DECLINE", details=str(offer_id), created_at=datetime.utcnow()))
    db.commit()
    ensure_three_judges(db, offer.dispute_id)
    return {"status": "ok"}


@router.get("/disputes/{dispute_id}")
def get_dispute(dispute_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    dispute = db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    flag_sla_missed(db, dispute_id)
    return {"dispute": dispute}


@router.post("/disputes/{dispute_id}/vote")
def vote_dispute(dispute_id: int, payload: JudgeVoteIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not payload.comment:
        raise HTTPException(status_code=400, detail="Comment required")
    if not payload.evidence_ref:
        raise HTTPException(status_code=400, detail="Evidence reference required")
    offer = db.query(JudgeOffer).filter(JudgeOffer.dispute_id == dispute_id, JudgeOffer.judge_user_id == user["id"]).first()
    if not offer or offer.status != "ACCEPTED":
        raise HTTPException(status_code=403, detail="Judge not accepted")
    vote = JudgeVote(dispute_id=dispute_id, judge_user_id=user["id"], vote=payload.vote, split=payload.split, comment=payload.comment)
    db.add(vote)
    db.add(AuditLog(actor_id=user["id"], action="JUDGE_VOTE", details=str(payload.model_dump()), created_at=datetime.utcnow()))
    # Auto-resolve when 2 votes exist with same decision (MVP rule)
    votes = db.query(JudgeVote).filter(JudgeVote.dispute_id == dispute_id).all()
    if len(votes) >= 2:
        v0 = votes[0].vote
        same = sum(1 for v in votes if v.vote == v0)
        if same >= 2:
            dispute = db.get(Dispute, dispute_id)
            if dispute:
                dispute.status = "RESOLVED"
                db.add(dispute)
                # In MVP, backend would call protocol executeDecision here
                sign_and_send_tx({"action": "execute_decision", "dispute_id": dispute_id, "decision": v0})
                quest = db.get(Quest, dispute.quest_id)
                if quest:
                    quest.status = "RESOLVED"
                    db.add(quest)
                # Experience records for judge/creator/worker on dispute resolution + ledger updates
                from app.services.experience import create_experience
                from app.models.task import Task
                from app.models.project import Project
                outcome_map = {
                    "SUCCESS": "SUCCESS",
                    "FAIL": "FAIL",
                    "SPLIT": "SPLIT",
                    "CREATOR": "FAIL",
                    "WORKER": "SUCCESS",
                }
                outcome = outcome_map.get(v0, "SPLIT")
                create_experience(db, user_id=user["id"], quest_id=dispute.quest_id, role="judge", outcome=outcome, was_disputed=True, dispute_result=v0)
                # Worker experience
                tasks = db.query(Task).filter(Task.quest_id == dispute.quest_id).all()
                payee_task = next((t for t in tasks if t.assigned_user_id and t.type == "HUMAN"), None)
                if payee_task:
                    create_experience(
                        db,
                        user_id=payee_task.assigned_user_id,
                        quest_id=dispute.quest_id,
                        role="worker",
                        outcome=outcome_map.get(v0, "SPLIT"),
                        was_disputed=True,
                        dispute_result=v0,
                        executor_type="HUMAN",
                    )
                # Creator experience
                if quest:
                    project = db.get(Project, quest.project_id)
                    if project:
                        creator_outcome = "SUCCESS" if v0 == "CREATOR" else ("SPLIT" if v0 == "SPLIT" else "FAIL")
                        create_experience(
                            db,
                            user_id=project.creator_id,
                            quest_id=dispute.quest_id,
                            role="creator",
                            outcome=creator_outcome,
                            was_disputed=True,
                            dispute_result=v0,
                        )
                        if quest.budget:
                            if v0 in ("SUCCESS", "WORKER") and payee_task:
                                record_release(db, quest_id=dispute.quest_id, user_id=payee_task.assigned_user_id, amount=quest.budget)
                            elif v0 in ("FAIL", "CREATOR"):
                                record_refund(db, quest_id=dispute.quest_id, user_id=project.creator_id, amount=quest.budget)
                            elif v0 == "SPLIT" and payee_task:
                                split_bps = payload.split if payload.split is not None else 5000
                                payee_amt = quest.budget * (split_bps / 10000.0)
                                payer_amt = quest.budget - payee_amt
                                record_split(db, quest_id=dispute.quest_id, user_id=payee_task.assigned_user_id, amount=payee_amt)
                                record_refund(db, quest_id=dispute.quest_id, user_id=project.creator_id, amount=payer_amt)
    db.commit()
    return {"status": "ok"}
