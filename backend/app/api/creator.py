from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.quest import Quest
from app.models.dispute import Dispute
from app.models.audit_log import AuditLog
from datetime import datetime
from app.schemas.project import ProjectCreate, ProjectOut
from app.schemas.proposal import ProposalOut
from app.schemas.quest import QuestFund, QuestAction
from app.services.auth import get_current_user
from app.services.judges import create_judge_offers_wave
from app.services.ledger import record_fund, record_release, record_credit
from app.services.privy import sign_and_send_tx
from app.core.config import settings
from app.models.payment import Payment
from app.schemas.payment import PaymentInit, PaymentUpdate
from app.services.moonpay import initiate_onramp, confirm_onramp
from app.services.pricing import compute_pricing
from app.services.state_machine import ensure, can_fund, can_approve, can_dispute

router = APIRouter()


@router.post("/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = Project(creator_id=user["id"], title=payload.title, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.post("/projects/{project_id}/proposals/generate", response_model=ProposalOut)
def generate_proposal(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # MVP: create a single quest proposal with buffer
    pricing = compute_pricing(worker_cost=1000, buffer_pct=20.0, moonpay_fee_pct=6.0)
    proposal_data = {
        "quests": [
            {
                "index": 1,
                "title": "Quest 1",
                "scope": "Definir alcance MVP",
                "budget": pricing.estimated_worker_cost,
                "buffer_pct": pricing.buffer_pct,
                "moonpay_fee_pct": pricing.moonpay_fee_pct,
                "price_to_creator": pricing.price_to_creator
            }
        ],
        "budget": pricing.estimated_worker_cost,
        "buffer_pct": pricing.buffer_pct,
        "moonpay_fee_pct": pricing.moonpay_fee_pct,
        "price_to_creator": pricing.price_to_creator,
        "assumptions": [],
        "questions": [],
    }
    proposal = Proposal(project_id=project_id, version=1, locked=False, data={
        **proposal_data
    })
    db.add(proposal)
    # Create quest draft in DB
    quest = Quest(project_id=project_id, index=1, scope_hash="scope_v1", budget=1000, status="DRAFT")
    db.add(quest)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/projects/{project_id}/proposals/{proposal_id}/approve", response_model=ProposalOut)
def approve_proposal(project_id: int, proposal_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.locked:
        raise HTTPException(status_code=400, detail="Proposal already locked")
    proposal.locked = True
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    proposals = db.query(Proposal).filter(Proposal.project_id == project_id).all()
    quests = db.query(Quest).filter(Quest.project_id == project_id).all()
    return {"project": project, "proposals": proposals, "quests": quests}


@router.post("/payments/initiate")
def initiate_payment(payload: PaymentInit, db: Session = Depends(get_db), user=Depends(get_current_user)):
    payment = Payment(creator_id=user["id"], quest_id=payload.quest_id, amount=payload.amount, fee=payload.amount * 0.06, status="INITIATED", created_at=datetime.utcnow())
    db.add(payment)
    db.commit()
    provider = initiate_onramp(payload.amount)
    return {"status": "ok", "payment_id": payment.id, "provider": provider["provider"], "fee": payment.fee}


@router.post("/payments/{payment_id}/confirm")
def confirm_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    prev_status = payment.status
    result = confirm_onramp(payment_id)
    payment.status = payload.status or result["status"]
    db.add(payment)
    db.commit()
    if payment.status == "USDC_CONFIRMED" and prev_status != "USDC_CONFIRMED":
        record_credit(db, user_id=payment.creator_id, amount=payment.amount, tx_hash=payment.provider or "")
    return {"status": "ok", "payment_id": payment.id, "payment_status": payment.status}


@router.post("/payments/{payment_id}/webhook")
def webhook_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    prev_status = payment.status
    payment.status = payload.status or payment.status
    db.add(payment)
    db.commit()
    if payment.status == "USDC_CONFIRMED" and prev_status != "USDC_CONFIRMED":
        record_credit(db, user_id=payment.creator_id, amount=payment.amount, tx_hash=payment.provider or "")
    return {"status": "ok"}


@router.post("/quests/{quest_id}/fund")
def fund_quest(quest_id: int, payload: QuestFund, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quest = db.get(Quest, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    payment = db.query(Payment).filter(Payment.quest_id == quest_id, Payment.creator_id == user["id"]).order_by(Payment.id.desc()).first()
    if not payment or payment.status != "USDC_CONFIRMED":
        raise HTTPException(status_code=400, detail="USDC not confirmed for funding")
    try:
        ensure(can_fund(quest.status), "Invalid status for funding")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # Scope freeze: if scope hash already set, it cannot change on funding
    if quest.scope_hash and quest.scope_hash != payload.scope_hash:
        raise HTTPException(status_code=400, detail="Scope hash immutable after funding")
    quest.scope_hash = payload.scope_hash
    quest.budget = payload.amount
    quest.status = "FUNDED"
    quest.funded_at = datetime.utcnow()
    db.add(quest)
    # Custodial on-chain fund (stub)
    sign_and_send_tx({"action": "fund", "quest_id": quest_id, "amount": payload.amount, "token": "USDC", "execution_type": "HUMAN"})
    record_fund(db, quest_id=quest_id, user_id=user["id"], amount=payload.amount)
    db.add(AuditLog(actor_id=user["id"], action="FUND_QUEST", details=str(payload.model_dump()), created_at=datetime.utcnow()))
    db.commit()
    return {"status": "ok"}


@router.post("/quests/{quest_id}/approve")
def approve_quest(quest_id: int, payload: QuestAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quest = db.get(Quest, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    try:
        ensure(can_approve(quest.status), "Quest not in review")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not payload.evidence_url:
        raise HTTPException(status_code=400, detail="Evidence required")
    payout = payload.payout_amount if payload.payout_amount is not None else quest.budget
    if payout > quest.budget:
        raise HTTPException(status_code=400, detail="Payout exceeds budget")
    quest.status = "APPROVED"
    db.add(quest)
    # Use refund-capable approval
    sign_and_send_tx({"action": "approve_with_refund", "quest_id": quest_id, "payout": payout})
    # Create experience records for HUMAN executor (worker) on success path
    from app.services.experience import create_experience
    from app.models.task import Task
    tasks = db.query(Task).filter(Task.quest_id == quest_id, Task.status == "SUBMITTED").all()
    payee_task = next((t for t in tasks if t.assigned_user_id and t.type == "HUMAN"), None)
    if payee_task:
        record_release(db, quest_id=quest_id, user_id=payee_task.assigned_user_id, amount=payout)
        create_experience(
            db,
            user_id=payee_task.assigned_user_id,
            quest_id=quest_id,
            role="worker",
            outcome="SUCCESS",
            was_disputed=False,
            dispute_result=None,
            executor_type="HUMAN",
        )
    create_experience(db, user_id=user["id"], quest_id=quest_id, role="creator", outcome="SUCCESS", was_disputed=False, dispute_result=None)
    db.add(AuditLog(actor_id=user["id"], action="APPROVE_QUEST", details=str(payload.model_dump()), created_at=datetime.utcnow()))
    db.commit()
    return {"status": "ok"}


@router.post("/quests/{quest_id}/dispute")
def dispute_quest(quest_id: int, payload: QuestAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quest = db.get(Quest, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    try:
        ensure(can_dispute(quest.status), "Cannot dispute in current status")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not payload.evidence_url:
        raise HTTPException(status_code=400, detail="Evidence required")
    dispute = Dispute(status="OPEN", quest_id=quest_id, opened_by=user["id"], reason=payload.reason or "", evidence=payload.evidence_url)
    db.add(dispute)
    quest.status = "DISPUTE"
    db.add(quest)
    sign_and_send_tx({"action": "open_dispute", "quest_id": quest_id, "evidence": payload.evidence_url})
    db.add(AuditLog(actor_id=user["id"], action="OPEN_DISPUTE_QUEST", details=str(payload.model_dump()), created_at=datetime.utcnow()))
    db.commit()
    create_judge_offers_wave(db, dispute.id)
    return {"status": "ok", "dispute_id": dispute.id}
