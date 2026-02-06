from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task import Task
from app.models.task_decline import TaskDecline
from app.schemas.task import TaskDecision, TaskSubmit
from app.schemas.worker import WorkerProfileUpdate
from app.models.worker_profile import WorkerProfile
from app.models.quest import Quest
from app.models.audit_log import AuditLog
from app.services.state_machine import ensure, can_submit_task, can_move_to_review
from app.services.auth import get_current_user

router = APIRouter()


@router.patch("/me/worker_profile")
def update_worker_profile(payload: WorkerProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user["id"]).first()
    if not profile:
        profile = WorkerProfile(user_id=user["id"])
    profile.skills = payload.skills
    profile.pricing = payload.pricing
    db.add(profile)
    db.commit()
    return {"status": "ok"}


@router.get("/worker/feed")
def worker_feed(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cutoff = datetime.utcnow() - timedelta(days=7)
    declined_task_ids = [
        d.task_id
        for d in db.query(TaskDecline)
        .filter(TaskDecline.user_id == user["id"], TaskDecline.declined_at >= cutoff)
        .all()
    ]
    query = db.query(Task).filter(Task.status == "OPEN")
    if declined_task_ids:
        query = query.filter(~Task.id.in_(declined_task_ids))
    tasks = query.all()
    return {"tasks": tasks}


@router.post("/tasks/{task_id}/accept")
def accept_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    active = db.query(Task).filter(Task.assigned_user_id == user["id"], Task.status == "ACTIVE").first()
    if active:
        raise HTTPException(status_code=400, detail="User already has active task")
    task = db.get(Task, task_id)
    if not task or task.status != "OPEN":
        raise HTTPException(status_code=400, detail="Task not available")
    task.status = "ACTIVE"
    task.assigned_user_id = user["id"]
    db.add(task)
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user["id"]).first()
    if profile:
        profile.active_task_id = task.id
        db.add(profile)
    db.commit()
    return {"status": "ok"}


@router.post("/tasks/{task_id}/decline")
def decline_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    decline = TaskDecline(task_id=task_id, user_id=user["id"], declined_at=datetime.utcnow())
    db.add(decline)
    db.commit()
    return {"status": "ok"}


@router.get("/tasks/active")
def active_task(db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = db.query(Task).filter(Task.assigned_user_id == user["id"], Task.status == "ACTIVE").first()
    return {"task": task}


@router.post("/tasks/{task_id}/submit")
def submit_task(task_id: int, payload: TaskSubmit, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not payload.evidence_url:
        raise HTTPException(status_code=400, detail="Evidence required")
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        ensure(can_submit_task(task.status), "Task not in active state")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    task.status = "SUBMITTED"
    db.add(task)
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user["id"]).first()
    if profile and profile.active_task_id == task.id:
        profile.active_task_id = None
        db.add(profile)
    db.add(AuditLog(actor_id=user["id"], action="SUBMIT_TASK", details=str(payload.model_dump()), created_at=datetime.utcnow()))
    # If all tasks for quest are submitted, move quest to REVIEW
    quest = db.get(Quest, task.quest_id)
    if quest:
        remaining = db.query(Task).filter(Task.quest_id == quest.id, Task.status != "SUBMITTED").count()
        if remaining == 0:
            try:
                ensure(can_move_to_review(quest.status), "Cannot move to review")
            except Exception as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            quest.status = "REVIEW"
            db.add(quest)
    db.commit()
    return {"status": "ok"}
