from fastapi import APIRouter, Depends
from app.schemas.user import UserOut, StatusUpdate
from app.schemas.withdrawal import MoonpayWithdrawRequest, ExternalWithdrawRequest, WithdrawalUpdate
from app.schemas.deposit import DepositInitiate, DepositWebhook
from app.schemas.balance import BalanceOut
from app.services.privy import sign_and_send_tx, create_custodial_wallet, get_wallet_address
from app.db.session import get_db
from app.models.withdrawal import Withdrawal
from app.models.deposit import Deposit
from app.models.user import User
from datetime import datetime
from app.core.config import settings
from app.services.auth import get_current_user
from app.services.balance import get_balance
from app.services.withdrawals import get_options, is_valid_address
from app.services.moonpay import initiate_onramp, initiate_offramp

router = APIRouter()


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user


@router.patch("/me/status", response_model=UserOut)
def update_status(payload: StatusUpdate, user=Depends(get_current_user)):
    user["status"] = payload.status
    return user


@router.get("/me/wallet")
def get_wallet(user=Depends(get_current_user), db=Depends(get_db)):
    wallet_id = create_custodial_wallet(user["id"])
    wallet_address = get_wallet_address(user["id"])
    existing = db.get(User, user["id"])
    if not existing:
        existing = User(id=user["id"], email=user["email"], status=user["status"], roles=user["roles"], wallet_address=wallet_address.lower())
        db.add(existing)
    else:
        if not existing.wallet_address:
            existing.wallet_address = wallet_address.lower()
            db.add(existing)
    db.commit()
    return {"wallet_id": wallet_id, "wallet_address": wallet_address}


@router.get("/wallet/balance", response_model=BalanceOut)
def wallet_balance(user=Depends(get_current_user), db=Depends(get_db)):
    bal = get_balance(db, user["id"])
    total = bal.available + bal.locked + bal.pending
    return BalanceOut(
        available_usdc=bal.available,
        locked_usdc=bal.locked,
        pending_withdrawals_usdc=bal.pending,
        total_usdc=total,
    )


@router.get("/withdrawal/options")
def withdrawal_options(country: str | None = None):
    options = get_options(country)
    return {"options": [o.__dict__ for o in options]}

@router.post("/wallet/deposit/initiate")
def initiate_deposit(payload: DepositInitiate, user=Depends(get_current_user), db=Depends(get_db)):
    if not settings.moonpay_enabled:
        return {"status": "error", "message": "MoonPay disabled"}
    if payload.amount_usd <= 0:
        return {"status": "error", "message": "Invalid amount"}
    deposit = Deposit(
        user_id=user["id"],
        amount_usd=payload.amount_usd,
        status="INITIATED",
        provider="MOONPAY",
        created_at=datetime.utcnow(),
    )
    db.add(deposit)
    db.commit()
    provider = initiate_onramp(payload.amount_usd, deposit.id)
    deposit.provider_session_id = provider.get("provider_session_id")
    db.add(deposit)
    db.commit()
    return {"status": "ok", "deposit_id": deposit.id, "provider_session_id": deposit.provider_session_id}


@router.post("/webhooks/moonpay")
def moonpay_webhook(payload: DepositWebhook, db=Depends(get_db)):
    deposit = db.get(Deposit, payload.deposit_id)
    if not deposit:
        return {"status": "error", "message": "Deposit not found"}
    deposit.status = payload.status
    if payload.provider_session_id:
        deposit.provider_session_id = payload.provider_session_id
    db.add(deposit)
    db.commit()
    if deposit.status == "USDC_CONFIRMED":
        from app.services.ledger import record_credit
        record_credit(db, user_id=deposit.user_id, amount=deposit.amount_usd, tx_hash=deposit.provider_session_id or "")
    return {"status": "ok"}


@router.post("/wallet/withdraw/moonpay")
def withdraw_moonpay(payload: MoonpayWithdrawRequest, user=Depends(get_current_user), db=Depends(get_db)):
    if not settings.moonpay_enabled:
        return {"status": "error", "message": "MoonPay disabled"}
    if payload.amount_usdc <= 0:
        return {"status": "error", "message": "Invalid amount"}
    bal = get_balance(db, user["id"])
    if payload.amount_usdc > bal.available:
        return {"status": "error", "message": "Insufficient available balance"}
    estimated_fee = max(payload.amount_usdc * settings.moonpay_fee_buffer_pct, settings.moonpay_fee_buffer_min_usd)
    estimated_net = max(0.0, payload.amount_usdc - estimated_fee)
    w = Withdrawal(
        user_id=user["id"],
        amount=payload.amount_usdc,
        method="moonpay",
        gross_usdc=payload.amount_usdc,
        estimated_fee_usd=estimated_fee,
        estimated_net_usd=estimated_net,
        status="REQUESTED",
        created_at=datetime.utcnow(),
    )
    db.add(w)
    db.commit()
    provider = initiate_offramp(payload.amount_usdc, w.id)
    w.provider_session_id = provider.get("provider_session_id")
    w.status = "PROCESSING"
    db.add(w)
    db.commit()
    return {"status": "ok", "withdrawal_id": w.id, "provider_session_id": w.provider_session_id, "estimated_fee_usd": estimated_fee, "estimated_net_usd": estimated_net}


@router.post("/wallet/withdraw/external")
def withdraw_external(payload: ExternalWithdrawRequest, user=Depends(get_current_user), db=Depends(get_db)):
    if not settings.withdraw_external_enabled:
        return {"status": "error", "message": "External withdrawals disabled"}
    if payload.amount_usdc <= 0:
        return {"status": "error", "message": "Invalid amount"}
    if not is_valid_address(payload.destination):
        return {"status": "error", "message": "Invalid destination address"}
    bal = get_balance(db, user["id"])
    if payload.amount_usdc > bal.available:
        return {"status": "error", "message": "Insufficient available balance"}
    w = Withdrawal(
        user_id=user["id"],
        amount=payload.amount_usdc,
        method="external",
        destination=payload.destination,
        status="REQUESTED",
        created_at=datetime.utcnow(),
    )
    db.add(w)
    db.commit()
    tx_hash = sign_and_send_tx({"to": payload.destination, "amount": payload.amount_usdc, "token": "USDC"})
    w.status = "SENT_ONCHAIN"
    w.tx_hash = tx_hash
    db.add(w)
    db.commit()
    return {"status": "ok", "withdrawal_id": w.id, "tx_hash": tx_hash}


@router.post("/withdrawals/{withdrawal_id}/send")
def send_withdrawal(withdrawal_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    w = db.get(Withdrawal, withdrawal_id)
    if not w:
        return {"status": "error", "message": "Not found"}
    if w.method != "external":
        return {"status": "error", "message": "Invalid method for send"}
    if w.status not in {"REQUESTED", "PROCESSING"}:
        return {"status": "error", "message": "Invalid status for send"}
    tx_hash = sign_and_send_tx({"to": w.destination, "amount": w.amount, "token": "USDC"})
    w.status = "SENT_ONCHAIN"
    w.tx_hash = tx_hash
    db.add(w)
    db.commit()
    return {"status": "ok", "tx": tx_hash}


@router.post("/withdrawals/{withdrawal_id}/mark_paid")
def mark_paid(withdrawal_id: int, payload: WithdrawalUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    w = db.get(Withdrawal, withdrawal_id)
    if not w:
        return {"status": "error", "message": "Not found"}
    w.status = payload.status
    if payload.tx_hash:
        w.tx_hash = payload.tx_hash
    db.add(w)
    db.commit()
    return {"status": "ok"}


@router.post("/withdrawals/{withdrawal_id}/process")
def process_withdrawal(withdrawal_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    w = db.get(Withdrawal, withdrawal_id)
    if not w:
        return {"status": "error", "message": "Not found"}
    if w.status not in {"REQUESTED", "PROCESSING"}:
        return {"status": "error", "message": "Invalid status for process"}
    if w.method == "moonpay":
        w.status = "PROCESSING"
        db.add(w)
        db.commit()
        return {"status": "ok", "method": "moonpay"}
    if w.method == "external":
        tx_hash = sign_and_send_tx({"to": w.destination, "amount": w.amount, "token": "USDC"})
        w.status = "SENT_ONCHAIN"
        w.tx_hash = tx_hash
        db.add(w)
        db.commit()
        return {"status": "ok", "tx": tx_hash}
    return {"status": "error", "message": "Unknown method"}
