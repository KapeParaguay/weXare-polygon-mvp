from sqlalchemy.orm import Session

from app.models.user import User
from app.services.privy import create_custodial_wallet, get_wallet_address


def ensure_user_wallet(db: Session, user_id: str, email: str | None = None, status: str | None = None, roles: str | None = None) -> tuple[str | None, str | None]:
    user = db.get(User, user_id)
    if user and user.wallet_id and user.wallet_address:
        return user.wallet_id, user.wallet_address

    wallet_id = None
    wallet_address = None
    try:
        wallet_id, wallet_address = create_custodial_wallet(user_id)
    except Exception:
        wallet_address = get_wallet_address(user_id)

    if not user:
        user = User(
            id=user_id,
            email=email or "",
            status=status or "ACTIVE",
            roles=roles or "",
            wallet_id=wallet_id,
            wallet_address=wallet_address.lower() if wallet_address else None,
        )
        db.add(user)
    else:
        if wallet_id and not user.wallet_id:
            user.wallet_id = wallet_id
        if wallet_address and not user.wallet_address:
            user.wallet_address = wallet_address.lower()
        db.add(user)
    db.commit()
    return user.wallet_id, user.wallet_address
