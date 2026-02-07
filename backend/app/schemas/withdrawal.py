from pydantic import BaseModel


class MoonpayWithdrawRequest(BaseModel):
    amount_usdc: float


class ExternalWithdrawRequest(BaseModel):
    amount_usdc: float
    destination: str


class WithdrawalUpdate(BaseModel):
    status: str
    tx_hash: str | None = None
