from pydantic import BaseModel


class PaymentInit(BaseModel):
    quest_id: int
    amount: float


class PaymentUpdate(BaseModel):
    status: str | None = None
