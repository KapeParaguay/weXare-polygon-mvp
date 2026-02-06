from pydantic import BaseModel


class WithdrawalRequest(BaseModel):
    amount: float
    method: str
    destination: str | None = None
    country: str | None = None


class WithdrawalUpdate(BaseModel):
    status: str
    coop_tx: str | None = None
