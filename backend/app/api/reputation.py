from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.reputation import ReputationOut
from app.services.reputation import calculate_reputation
from app.services.auth import get_current_user

router = APIRouter()
_last_req: dict[str, float] = {}


@router.get("/reputation/{user_id}", response_model=ReputationOut)
def get_reputation(user_id: str, role: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    import time
    key = f"{user_id}:{role or 'worker'}"
    now = time.time()
    if key in _last_req and now - _last_req[key] < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit")
    _last_req[key] = now
    role_val = role or "worker"
    rep = calculate_reputation(db, user_id, role_val)
    return ReputationOut(user_id=rep.user_id, role=rep.role, score=rep.score, formula_version=rep.formula_version)
