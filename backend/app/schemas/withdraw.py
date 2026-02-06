from pydantic import BaseModel


class WithdrawRequest(BaseModel):
    amount: float
