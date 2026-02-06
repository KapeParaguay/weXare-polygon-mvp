from fastapi import APIRouter, Depends
from app.schemas.user import UserOut, StatusUpdate
from app.schemas.withdrawal import WithdrawalRequest, WithdrawalUpdate
from app.schemas.balance import BalanceOut
from app.services.privy import sign_and_send_tx, create_custodial_wallet, get_wallet_address
from app.db.session import get_db
from app.models.withdrawal import Withdrawal
from app.models.user import User
from datetime import datetime
from app.core.config import settings
from app.services.auth import get_current_user
from app.services.balance import get_balance
from app.services.withdrawals import get_options, is_valid_address

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
    return BalanceOut(available=bal.available, locked=bal.locked, pending=bal.pending)


@router.get("/withdrawal/options")
def withdrawal_options(country: str | None = None):
    options = get_options(country)
    return {"options": [o.__dict__ for o in options]}


@router.post("/wallet/withdraw")
def withdraw(payload: WithdrawalRequest, user=Depends(get_current_user), db=Depends(get_db)):
    if not settings.cooperative_withdrawal_address:
        return {"status": "error", "message": "Cooperative address not configured"}
    if payload.method not in {"bank", "crypto", "moonpay"}:
        return {"status": "error", "message": "Invalid withdrawal method"}
    if payload.amount <= 0:
        return {"status": "error", "message": "Invalid amount"}
    bal = get_balance(db, user["id"])
    if payload.amount > bal.available:
        return {"status": "error", "message": "Insufficient available balance"}
    if payload.method == "crypto":
        if not payload.destination or not is_valid_address(payload.destination):
            return {"status": "error", "message": "Invalid destination address"}
    w = Withdrawal(
        user_id=user["id"],
        amount=payload.amount,
        method=payload.method,
        destination=payload.destination,
        country=payload.country,
        status="REQUESTED",
        created_at=datetime.utcnow(),
    )
    db.add(w)
    db.commit()
    return {"status": "ok", "withdrawal_id": w.id}


@router.post("/withdrawals/{withdrawal_id}/send")
def send_withdrawal(withdrawal_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    w = db.get(Withdrawal, withdrawal_id)
    if not w:
        return {"status": "error", "message": "Not found"}
    if w.method != "crypto" and w.method != "bank":
        return {"status": "error", "message": "Invalid method for send"}
    if w.status not in {"REQUESTED", "PROCESSING"}:
        return {"status": "error", "message": "Invalid status for send"}
    tx_hash = sign_and_send_tx(
        {"to": settings.cooperative_withdrawal_address if w.method == "bank" else w.destination, "amount": w.amount, "token": "USDC"}
    )
    w.status = "SENT_ONCHAIN"
    w.coop_tx = tx_hash
    db.add(w)
    db.commit()
    return {"status": "ok", "tx": tx_hash}


@router.post("/withdrawals/{withdrawal_id}/mark_paid")
def mark_paid(withdrawal_id: int, payload: WithdrawalUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    w = db.get(Withdrawal, withdrawal_id)
    if not w:
        return {"status": "error", "message": "Not found"}
    w.status = payload.status
    if payload.coop_tx:
        w.coop_tx = payload.coop_tx
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
    if w.method == "bank":
        w.status = "PROCESSING"
        db.add(w)
        db.commit()
        return {"status": "ok", "method": "bank"}
    if w.method == "crypto":
        tx_hash = sign_and_send_tx({"to": w.destination, "amount": w.amount, "token": "USDC"})
        w.status = "SENT_ONCHAIN"
        w.coop_tx = tx_hash
        db.add(w)
        db.commit()
        return {"status": "ok", "tx": tx_hash}
    if w.method == "moonpay":
        w.status = "PROCESSING"
        db.add(w)
        db.commit()
        return {"status": "ok", "method": "moonpay"}
    return {"status": "error", "message": "Unknown method"}
