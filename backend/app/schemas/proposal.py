from pydantic import BaseModel


class ProposalOut(BaseModel):
    id: int
    version: int
    locked: bool
    data: dict
