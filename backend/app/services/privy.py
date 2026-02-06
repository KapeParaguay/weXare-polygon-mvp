"""Privy integration stub (server-side custody).
In production, use Privy server-side SDK or API to create wallets and sign txs.
"""

import hashlib
from app.core.config import settings


def create_custodial_wallet(user_id: str) -> str:
    # Returns custodial wallet id
    return f"privy_wallet_{user_id}"


def get_wallet_address(user_id: str) -> str:
    # MVP deterministic placeholder address derived from user_id
    h = hashlib.sha256(user_id.encode()).hexdigest()[:40]
    return f"0x{h}"


def sign_and_send_tx(payload: dict) -> str:
    # Placeholder for Privy signing flow
    return "0xTX_HASH_PLACEHOLDER"
