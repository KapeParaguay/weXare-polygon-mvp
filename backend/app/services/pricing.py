from dataclasses import dataclass
from app.core.config import settings


@dataclass
class Pricing:
    estimated_worker_cost: float
    buffer_pct: float
    moonpay_fee_pct: float

    @property
    def buffer_amount(self) -> float:
        return self.estimated_worker_cost * (self.buffer_pct / 100.0)

    @property
    def moonpay_fee(self) -> float:
        base = self.estimated_worker_cost + self.buffer_amount
        pct_fee = base * (self.moonpay_fee_pct / 100.0)
        return max(pct_fee, settings.moonpay_fee_buffer_min_usd)

    @property
    def price_to_creator(self) -> float:
        return self.estimated_worker_cost + self.buffer_amount + self.moonpay_fee


def compute_pricing(worker_cost: float, buffer_pct: float = 20.0, moonpay_fee_pct: float | None = None) -> Pricing:
    fee_pct = moonpay_fee_pct if moonpay_fee_pct is not None else settings.moonpay_fee_buffer_pct * 100.0
    return Pricing(estimated_worker_cost=worker_cost, buffer_pct=buffer_pct, moonpay_fee_pct=fee_pct)
