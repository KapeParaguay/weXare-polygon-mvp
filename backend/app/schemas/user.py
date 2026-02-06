from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    email: str
    status: str
    roles: str


class StatusUpdate(BaseModel):
    status: str
