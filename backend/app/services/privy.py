"""Privy integration (server-side custody via REST)."""

from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from web3 import Web3

from app.core.config import settings


ESCROW_ABI = [
    {
        "inputs": [
            {"name": "questId", "type": "uint256"},
            {"name": "parentQuestId", "type": "uint256"},
            {"name": "payer", "type": "address"},
            {"name": "payee", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "scopeHash", "type": "bytes32"},
            {"name": "executionType", "type": "uint8"},
        ],
        "name": "fundQuest",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "questId", "type": "uint256"}],
        "name": "approveQuest",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "questId", "type": "uint256"},
            {"name": "disputeId", "type": "uint256"},
            {"name": "evidenceCreator", "type": "bytes32"},
            {"name": "evidenceWorker", "type": "bytes32"},
        ],
        "name": "openDispute",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "questId", "type": "uint256"},
            {"name": "decisionType", "type": "uint8"},
            {"name": "splitBps", "type": "uint16"},
        ],
        "name": "executeQuest",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

DISPUTE_ABI = [
    {
        "inputs": [
            {"name": "disputeId", "type": "uint256"},
            {"name": "judge1", "type": "address"},
            {"name": "judge2", "type": "address"},
            {"name": "judge3", "type": "address"},
        ],
        "name": "assignJudges",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "disputeId", "type": "uint256"},
            {"name": "voteType", "type": "uint8"},
            {"name": "splitBps", "type": "uint16"},
            {"name": "commentHash", "type": "bytes32"},
        ],
        "name": "submitVote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "disputeId", "type": "uint256"}],
        "name": "finalizeAndExecute",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

USDC_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


def _basic_auth_header() -> str:
    token = f"{settings.privy_app_id}:{settings.privy_app_secret}".encode()
    return "Basic " + base64.b64encode(token).decode()


def _sign_request(method: str, url: str, body: dict | None) -> tuple[str, str]:
    if not settings.privy_auth_key:
        return "", ""
    ts = str(int(time.time()))
    payload = "" if body is None else json.dumps(body, separators=(",", ":"), sort_keys=True)
    message = f"{method.upper()}|{url}|{payload}|{ts}".encode()
    key = serialization.load_pem_private_key(
        settings.privy_auth_key.encode(),
        password=None,
    )
    assert isinstance(key, ec.EllipticCurvePrivateKey)
    signature = key.sign(message, ec.ECDSA(hashes.SHA256()))
    return ts, base64.b64encode(signature).decode()


def _privy_request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{settings.privy_api_base.rstrip('/')}{path}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": _basic_auth_header(),
        "privy-app-id": settings.privy_app_id,
    }
    ts, sig = _sign_request(method, url, body)
    if sig:
        headers["privy-authorization-signature"] = f"v1,{ts},{sig}"

    with httpx.Client(timeout=30) as client:
        resp = client.request(method, url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()


def create_custodial_wallet(user_id: str) -> tuple[str, str]:
    if not settings.privy_app_id or not settings.privy_app_secret:
        raise RuntimeError("Missing PRIVY_APP_ID/PRIVY_APP_SECRET")
    payload = {
        "chain_type": "ethereum",
        "label": f"user:{user_id}",
    }
    data = _privy_request("POST", "/v1/wallets", payload)
    wallet_id = data.get("id") or data.get("wallet_id")
    address = (data.get("address") or "").lower()
    if not wallet_id or not address:
        raise RuntimeError("Privy wallet creation failed")
    return wallet_id, address


def get_wallet_address(user_id: str) -> str:
    # Backward-compat fallback for local/dev
    h = hashlib.sha256(user_id.encode()).hexdigest()[:40]
    return f"0x{h}"


def _to_bytes32(value: str | None) -> bytes:
    if not value:
        return b"\x00" * 32
    if value.startswith("0x") and len(value) == 66:
        return bytes.fromhex(value[2:])
    return Web3.keccak(text=value)


def _encode_contract_call(address: str, abi: list[dict], fn: str, args: list[Any]) -> str:
    w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    return contract.encodeABI(fn_name=fn, args=args)


def _send_wallet_rpc(wallet_id: str, to: str, data: str, value_wei: int = 0) -> str:
    body = {
        "method": "eth_sendTransaction",
        "params": [
            {
                "to": to,
                "data": data,
                "value": hex(value_wei),
            }
        ],
        "chain_type": "ethereum",
        "caip2": f"eip155:{settings.chain_id}",
    }
    resp = _privy_request("POST", f"/v1/wallets/{wallet_id}/rpc", body)
    tx_hash = resp.get("result") or resp.get("txHash") or resp.get("transaction_hash")
    if not tx_hash:
        raise RuntimeError(f"Privy RPC error: {resp}")
    return tx_hash


def sign_and_send_tx(payload: dict) -> str:
    if not settings.privy_wallet_id or not settings.rpc_url or not settings.privy_app_id or not settings.privy_app_secret:
        return "0xTX_HASH_PLACEHOLDER"

    action = payload.get("action")
    wallet_id = payload.get("wallet_id") or settings.privy_wallet_id

    if payload.get("token") == "USDC" and payload.get("to"):
        to_addr = payload["to"]
        amount = int(float(payload.get("amount", 0)) * 10**6)
        data = _encode_contract_call(settings.usdc_token_address, USDC_ABI, "transfer", [to_addr, amount])
        return _send_wallet_rpc(wallet_id, settings.usdc_token_address, data)

    if action == "fund":
        if not settings.escrow_manager_address:
            raise RuntimeError("Missing ESCROW_MANAGER_ADDRESS")
        if not settings.coop_wallet_address:
            raise RuntimeError("Missing COOP_WALLET_ADDRESS")
        payer = settings.privy_wallet_address or ""
        if not payer:
            raise RuntimeError("Missing PRIVY_WALLET_ADDRESS")
        quest_id = int(payload["quest_id"])
        parent_id = int(payload.get("parent_quest_id") or 0)
        amount = int(float(payload.get("amount", 0)) * 10**6)
        scope_hash = _to_bytes32(payload.get("scope_hash"))
        execution_type = 0 if payload.get("execution_type") == "HUMAN" else 1
        # Approve USDC first
        approve_data = _encode_contract_call(settings.usdc_token_address, USDC_ABI, "approve", [settings.escrow_manager_address, amount])
        _send_wallet_rpc(wallet_id, settings.usdc_token_address, approve_data)
        data = _encode_contract_call(
            settings.escrow_manager_address,
            ESCROW_ABI,
            "fundQuest",
            [quest_id, parent_id, payer, settings.coop_wallet_address, amount, scope_hash, execution_type],
        )
        return _send_wallet_rpc(wallet_id, settings.escrow_manager_address, data)

    if action == "approve_with_refund" or action == "approve":
        if not settings.escrow_manager_address:
            raise RuntimeError("Missing ESCROW_MANAGER_ADDRESS")
        quest_id = int(payload["quest_id"])
        data = _encode_contract_call(settings.escrow_manager_address, ESCROW_ABI, "approveQuest", [quest_id])
        _send_wallet_rpc(wallet_id, settings.escrow_manager_address, data)
        # Execute with SUCCESS (full payout) on-chain
        exec_data = _encode_contract_call(settings.escrow_manager_address, ESCROW_ABI, "executeQuest", [quest_id, 1, 0])
        return _send_wallet_rpc(wallet_id, settings.escrow_manager_address, exec_data)

    if action == "open_dispute":
        if not settings.escrow_manager_address:
            raise RuntimeError("Missing ESCROW_MANAGER_ADDRESS")
        quest_id = int(payload["quest_id"])
        dispute_id = int(payload["dispute_id"])
        evidence = payload.get("evidence")
        evidence_hash_creator = _to_bytes32(evidence)
        evidence_hash_worker = b"\x00" * 32
        data = _encode_contract_call(
            settings.escrow_manager_address,
            ESCROW_ABI,
            "openDispute",
            [quest_id, dispute_id, evidence_hash_creator, evidence_hash_worker],
        )
        return _send_wallet_rpc(wallet_id, settings.escrow_manager_address, data)

    if action == "assign_judges":
        if not settings.dispute_manager_address:
            raise RuntimeError("Missing DISPUTE_MANAGER_ADDRESS")
        dispute_id = int(payload["dispute_id"])
        judges = payload["judges"]
        data = _encode_contract_call(settings.dispute_manager_address, DISPUTE_ABI, "assignJudges", [dispute_id, *judges])
        return _send_wallet_rpc(wallet_id, settings.dispute_manager_address, data)

    if action == "submit_vote":
        if not settings.dispute_manager_address:
            raise RuntimeError("Missing DISPUTE_MANAGER_ADDRESS")
        dispute_id = int(payload["dispute_id"])
        vote_type = int(payload["vote_type"])
        split_bps = int(payload.get("split_bps") or 0)
        comment_hash = _to_bytes32(payload.get("comment"))
        data = _encode_contract_call(
            settings.dispute_manager_address,
            DISPUTE_ABI,
            "submitVote",
            [dispute_id, vote_type, split_bps, comment_hash],
        )
        return _send_wallet_rpc(wallet_id, settings.dispute_manager_address, data)

    if action == "finalize_execute":
        if not settings.dispute_manager_address:
            raise RuntimeError("Missing DISPUTE_MANAGER_ADDRESS")
        dispute_id = int(payload["dispute_id"])
        data = _encode_contract_call(settings.dispute_manager_address, DISPUTE_ABI, "finalizeAndExecute", [dispute_id])
        return _send_wallet_rpc(wallet_id, settings.dispute_manager_address, data)

    return "0xTX_HASH_PLACEHOLDER"
