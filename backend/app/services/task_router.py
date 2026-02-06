from datetime import datetime
from sqlalchemy.orm import Session
from app.models.quest import Quest
from app.models.task import Task
from app.models.skill_run import SkillRun
from app.services.skills import run_skill


def route_quest(db: Session, quest_id: int, skill_type: str) -> dict:
    quest = db.get(Quest, quest_id)
    if not quest:
        return {"status": "error", "message": "Quest not found"}

    # Try AUTO
    result = run_skill(skill_type, context={"quest_id": quest_id})
    db.add(SkillRun(quest_id=quest_id, skill_type=skill_type, status=result.status, artifact_url=result.artifact_url, created_at=datetime.utcnow()))

    if result.status == "success":
        return {"status": "auto_success", "artifact": result.artifact_url}

    # Fallback to HUMAN
    task = Task(quest_id=quest_id, type="HUMAN", status="OPEN", assigned_user_id=None)
    db.add(task)
    db.commit()
    return {"status": "needs_human", "task_id": task.id}
