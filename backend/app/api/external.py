from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/offers/{token}")
def get_offer(token: str):
    return {"token": token, "status": "PENDING"}


@router.post("/offers/{token}/accept")
def accept_offer(token: str):
    return {"status": "ok"}


@router.get("/config")
def public_config():
    return {
        "onchain_node_fee_usd": settings.onchain_node_fee_usd,
        "moonpay_fee_buffer_pct": settings.moonpay_fee_buffer_pct,
        "moonpay_fee_buffer_min_usd": settings.moonpay_fee_buffer_min_usd,
    }
