from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.task_router import route_quest
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/skills/run")
def run_skill(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    quest_id = payload.get("quest_id")
    skill_type = payload.get("skill_type", "writing")
    return route_quest(db, quest_id, skill_type)
