from pydantic import BaseModel


class BalanceOut(BaseModel):
    available: float
    locked: float
    pending: float
