import os
import pytest
from web3 import Web3

from app.workers.indexer import process_events
from app.models.user import User
from app.models.quest import Quest
from app.models.dispute import Dispute
from app.models.escrow_ledger import EscrowLedger
from app.core.config import settings

RUN = os.getenv("RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(not RUN, reason="E2E tests require RUN_E2E=1")

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
        "inputs": [
            {"name": "questId", "type": "uint256"},
            {"name": "evidenceHash", "type": "bytes32"},
        ],
        "name": "submitQuest",
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
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]


def test_e2e_fund_dispute_execute_with_indexer(db_session):
    rpc = os.getenv("RPC_URL")
    escrow_addr = os.getenv("ESCROW_MANAGER_ADDRESS")
    dispute_addr = os.getenv("DISPUTE_MANAGER_ADDRESS")
    usdc_addr = os.getenv("USDC_TOKEN_ADDRESS")
    if not rpc or not escrow_addr or not dispute_addr or not usdc_addr:
        pytest.skip("Missing RPC_URL/ESCROW_MANAGER_ADDRESS/DISPUTE_MANAGER_ADDRESS/USDC_TOKEN_ADDRESS")

    settings.rpc_url = rpc
    settings.escrow_manager_address = escrow_addr
    settings.dispute_manager_address = dispute_addr

    w3 = Web3(Web3.HTTPProvider(rpc))
    accounts = w3.eth.accounts
    operator = accounts[0]
    payer = accounts[1]
    payee = accounts[2]
    judge1 = accounts[3]
    judge2 = accounts[4]
    judge3 = accounts[5]

    escrow = w3.eth.contract(address=Web3.to_checksum_address(escrow_addr), abi=ESCROW_ABI)
    dispute = w3.eth.contract(address=Web3.to_checksum_address(dispute_addr), abi=DISPUTE_ABI)
    usdc = w3.eth.contract(address=Web3.to_checksum_address(usdc_addr), abi=USDC_ABI)

    # Seed DB user + quest + dispute
    db_session.add(User(id="user_payer", email="payer@example.com", status="ACTIVE", roles="CREATOR", wallet_address=payer.lower()))
    db_session.add(Quest(id=1, project_id=1, parent_quest_id=None, index=1, scope_hash="scope", budget=100, status="DRAFT"))
    db_session.add(Dispute(id=11, quest_id=1, status="OPEN", opened_by="user_payer", reason="", evidence=""))
    db_session.commit()

    # Mint USDC and approve
    usdc.functions.mint(payer, 1_000_000 * 10**6).transact({"from": operator})
    usdc.functions.approve(escrow_addr, 1_000_000 * 10**6).transact({"from": payer})

    scope_hash = Web3.keccak(text="scope")
    escrow.functions.fundQuest(1, 0, payer, payee, 100 * 10**6, scope_hash, 0).transact({"from": operator})
    escrow.functions.openDispute(1, 11, Web3.keccak(text="c"), Web3.keccak(text="w")).transact({"from": operator})

    dispute.functions.assignJudges(11, judge1, judge2, judge3).transact({"from": operator})
    dispute.functions.submitVote(11, 1, 0, Web3.keccak(text="v1")).transact({"from": judge1})
    dispute.functions.submitVote(11, 1, 0, Web3.keccak(text="v2")).transact({"from": judge2})
    dispute.functions.finalizeAndExecute(11).transact({"from": operator})

    # Indexer processes events and updates DB/ledger
    latest = w3.eth.block_number
    process_events(w3, db_session, 0, latest)

    # Assert on-chain payee got paid
    payee_bal = usdc.functions.balanceOf(payee).call()
    assert payee_bal == 100 * 10**6

    # Assert DB ledger recorded fund
    entries = db_session.query(EscrowLedger).filter(EscrowLedger.quest_id == 1, EscrowLedger.kind == "FUND").all()
    assert len(entries) == 1
