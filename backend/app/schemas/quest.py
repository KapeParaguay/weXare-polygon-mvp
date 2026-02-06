from pydantic import BaseModel


class QuestFund(BaseModel):
    quest_id: int
    scope_hash: str
    amount: float


class QuestAction(BaseModel):
    quest_id: int
    evidence_url: str | None = None
    reason: str | None = None
    payout_amount: float | None = None
