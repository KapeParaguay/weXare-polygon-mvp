from pydantic import BaseModel


class TaskDecision(BaseModel):
    task_id: int


class TaskSubmit(BaseModel):
    task_id: int
    evidence_url: str
