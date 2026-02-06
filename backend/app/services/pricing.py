from dataclasses import dataclass


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
        return (self.estimated_worker_cost + self.buffer_amount) * (self.moonpay_fee_pct / 100.0)

    @property
    def price_to_creator(self) -> float:
        return self.estimated_worker_cost + self.buffer_amount + self.moonpay_fee


def compute_pricing(worker_cost: float, buffer_pct: float = 20.0, moonpay_fee_pct: float = 6.0) -> Pricing:
    return Pricing(estimated_worker_cost=worker_cost, buffer_pct=buffer_pct, moonpay_fee_pct=moonpay_fee_pct)
