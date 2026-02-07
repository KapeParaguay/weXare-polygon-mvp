from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.task import Task
from app.models.task_decline import TaskDecline
from app.models.judge_offer import JudgeOffer
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/feed")
def unified_feed(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cutoff = datetime.utcnow() - timedelta(days=7)
    declined_task_ids = [
        d.task_id
        for d in db.query(TaskDecline)
        .filter(TaskDecline.user_id == user["id"], TaskDecline.declined_at >= cutoff)
        .all()
    ]
    tasks_q = db.query(Task).filter(Task.status == "OPEN")
    if declined_task_ids:
        tasks_q = tasks_q.filter(~Task.id.in_(declined_task_ids))
    tasks = tasks_q.all()

    offers = db.query(JudgeOffer).filter(JudgeOffer.judge_user_id == user["id"], JudgeOffer.status == "PENDING").all()

    cards = []
    for t in tasks:
        cards.append({"type": "work", "id": t.id, "quest_id": t.quest_id, "title": f"Quest #{t.quest_id}", "status": t.status})
    for o in offers:
        cards.append({"type": "judge", "id": o.id, "dispute_id": o.dispute_id, "title": f"Dispute #{o.dispute_id}", "status": o.status})

    return {"cards": cards}
