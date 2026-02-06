import time
from web3 import Web3
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.indexer_state import IndexerState
from app.models.quest import Quest
from app.models.dispute import Dispute
from app.models.user import User
from app.services.ledger import record_fund


ESCROW_EVENTS_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "questId", "type": "uint256"},
            {"indexed": False, "name": "parentQuestId", "type": "uint256"},
            {"indexed": False, "name": "payer", "type": "address"},
            {"indexed": False, "name": "payee", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"},
            {"indexed": False, "name": "scopeHash", "type": "bytes32"},
        ],
        "name": "QuestFunded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "questId", "type": "uint256"},
            {"indexed": False, "name": "decisionType", "type": "uint8"},
            {"indexed": False, "name": "splitBps", "type": "uint16"},
            {"indexed": False, "name": "payerAmount", "type": "uint256"},
            {"indexed": False, "name": "payeeAmount", "type": "uint256"},
        ],
        "name": "QuestExecuted",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "questId", "type": "uint256"},
            {"indexed": False, "name": "disputeId", "type": "uint256"},
        ],
        "name": "QuestDisputed",
        "type": "event",
    },
]

DISPUTE_EVENTS_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "disputeId", "type": "uint256"},
            {"indexed": False, "name": "questId", "type": "uint256"},
            {"indexed": False, "name": "evidenceCreator", "type": "bytes32"},
            {"indexed": False, "name": "evidenceWorker", "type": "bytes32"},
        ],
        "name": "DisputeCreated",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "disputeId", "type": "uint256"},
            {"indexed": False, "name": "decisionType", "type": "uint8"},
            {"indexed": False, "name": "splitBps", "type": "uint16"},
        ],
        "name": "DisputeResolved",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "disputeId", "type": "uint256"},
        ],
        "name": "DisputeExecuted",
        "type": "event",
    },
]


def _get_state(db: Session, key: str, default: int) -> int:
    row = db.query(IndexerState).filter(IndexerState.key == key).first()
    if not row:
        row = IndexerState(key=key, value=str(default))
        db.add(row)
        db.commit()
        return default
    try:
        return int(row.value)
    except ValueError:
        return default


def _set_state(db: Session, key: str, value: int) -> None:
    row = db.query(IndexerState).filter(IndexerState.key == key).first()
    if not row:
        row = IndexerState(key=key, value=str(value))
        db.add(row)
    else:
        row.value = str(value)
        db.add(row)
    db.commit()


def _user_id_for_address(db: Session, addr: str) -> str | None:
    if not addr:
        return None
    user = db.query(User).filter(User.wallet_address == addr.lower()).first()
    return user.id if user else None


def process_events(w3: Web3, db: Session, from_block: int, to_block: int) -> None:
    escrow = w3.eth.contract(address=Web3.to_checksum_address(settings.escrow_manager_address), abi=ESCROW_EVENTS_ABI)
    dispute = w3.eth.contract(address=Web3.to_checksum_address(settings.dispute_manager_address), abi=DISPUTE_EVENTS_ABI)

    for event in escrow.events.QuestFunded().get_logs(fromBlock=from_block, toBlock=to_block):
        quest_id = int(event["args"]["questId"])
        payer = event["args"]["payer"]
        amount = float(event["args"]["amount"]) / 1e6
        q = db.get(Quest, quest_id)
        if q:
            q.status = "FUNDED"
            db.add(q)
        user_id = _user_id_for_address(db, payer)
        if user_id:
            record_fund(db, quest_id=quest_id, user_id=user_id, amount=amount, tx_hash=event["transactionHash"].hex())

    for event in escrow.events.QuestExecuted().get_logs(fromBlock=from_block, toBlock=to_block):
        quest_id = int(event["args"]["questId"])
        q = db.get(Quest, quest_id)
        if q:
            q.status = "EXECUTED"
            db.add(q)
        # NOTE: QuestExecuted event does not include payer/payee addresses.
        # Ledger sync for execution requires mapping payee/payer off-chain.

    for event in escrow.events.QuestDisputed().get_logs(fromBlock=from_block, toBlock=to_block):
        quest_id = int(event["args"]["questId"])
        q = db.get(Quest, quest_id)
        if q:
            q.status = "DISPUTE"
            db.add(q)

    for event in dispute.events.DisputeCreated().get_logs(fromBlock=from_block, toBlock=to_block):
        dispute_id = int(event["args"]["disputeId"])
        d = db.get(Dispute, dispute_id)
        if d:
            d.status = "OPEN"
            db.add(d)

    for event in dispute.events.DisputeResolved().get_logs(fromBlock=from_block, toBlock=to_block):
        dispute_id = int(event["args"]["disputeId"])
        d = db.get(Dispute, dispute_id)
        if d:
            d.status = "RESOLVED"
            db.add(d)

    for event in dispute.events.DisputeExecuted().get_logs(fromBlock=from_block, toBlock=to_block):
        dispute_id = int(event["args"]["disputeId"])
        d = db.get(Dispute, dispute_id)
        if d:
            d.status = "EXECUTED"
            db.add(d)

    db.commit()


def run_indexer() -> None:
    if not settings.rpc_url or not settings.escrow_manager_address or not settings.dispute_manager_address:
        raise RuntimeError("Indexer requires RPC_URL, ESCROW_MANAGER_ADDRESS, DISPUTE_MANAGER_ADDRESS")

    w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
    db = SessionLocal()
    try:
        start_block = settings.indexer_start_block or w3.eth.block_number
        last_block = _get_state(db, "last_block", start_block)

        while True:
            latest = w3.eth.block_number
            if latest > last_block:
                from_block = last_block + 1
                to_block = latest
                process_events(w3, db, from_block, to_block)
                _set_state(db, "last_block", latest)
                last_block = latest

            time.sleep(settings.indexer_poll_sec)
    finally:
        db.close()


if __name__ == "__main__":
    run_indexer()
