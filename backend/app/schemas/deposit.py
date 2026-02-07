from pydantic import BaseModel


class DepositInitiate(BaseModel):
    amount_usd: float


class DepositWebhook(BaseModel):
    deposit_id: int
    status: str
    provider_session_id: str | None = None
