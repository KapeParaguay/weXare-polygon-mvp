from pydantic import BaseModel


class WorkerProfileUpdate(BaseModel):
    skills: list[str] = []
    pricing: float = 0.0
    status: str | None = None
