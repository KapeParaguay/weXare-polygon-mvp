from pydantic import BaseModel


class BalanceOut(BaseModel):
    available_usdc: float
    locked_usdc: float
    pending_withdrawals_usdc: float
    total_usdc: float
