from pydantic import BaseModel


class JudgeDecision(BaseModel):
    offer_id: int


class JudgeVoteIn(BaseModel):
    dispute_id: int
    vote: str
    split: int = 0
    comment: str
    evidence_ref: str
