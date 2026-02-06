"""MoonPay on-ramp stub for MVP."""


def initiate_onramp(amount: float) -> dict:
    return {"provider": "MOONPAY", "status": "INITIATED", "amount": amount}


def confirm_onramp(payment_id: int) -> dict:
    return {"payment_id": payment_id, "status": "USDC_CONFIRMED"}
