from pydantic import BaseModel


class ReputationOut(BaseModel):
    user_id: str
    role: str
    score: float
    formula_version: str
