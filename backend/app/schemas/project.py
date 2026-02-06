from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
