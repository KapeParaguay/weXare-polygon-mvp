"""MoonPay on/off-ramp stub for MVP."""


def initiate_onramp(amount: float, deposit_id: int) -> dict:
    return {"provider": "MOONPAY", "status": "INITIATED", "amount": amount, "provider_session_id": f"moonpay_on_{deposit_id}"}


def initiate_offramp(amount: float, withdrawal_id: int) -> dict:
    return {"provider": "MOONPAY", "status": "PROCESSING", "amount": amount, "provider_session_id": f"moonpay_off_{withdrawal_id}"}


def confirm_onramp(payment_id: int) -> dict:
    return {"payment_id": payment_id, "status": "USDC_CONFIRMED"}
