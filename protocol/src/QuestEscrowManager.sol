// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
import "openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol";
import "openzeppelin-contracts/contracts/utils/Pausable.sol";
import "openzeppelin-contracts/contracts/access/AccessControl.sol";

interface IQuestDisputeManager {
    function getDecision(uint256 disputeId) external view returns (bool, uint8, uint16);
}

contract QuestEscrowManager is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    enum QuestStatus { NONE, FUNDED, SUBMITTED, APPROVED, DISPUTED, RESOLVED, EXECUTED, CANCELLED }
    enum DecisionType { NONE, SUCCESS, FAIL, SPLIT }
    enum ExecutionType { HUMAN, AUTO }

    struct QuestEscrow {
        uint256 questId;
        uint256 parentQuestId;
        address payer;
        address payee;
        uint256 amount;
        bytes32 scopeHash;
        QuestStatus status;
        uint256 disputeId;
        uint64 fundedAt;
        bool executed;
        DecisionType decisionType;
        uint16 decisionSplitBps;
        ExecutionType executionType;
    }

    IERC20 public immutable usdc;
    IQuestDisputeManager public disputeManager;
    address public cooperativeWallet;

    mapping(uint256 => QuestEscrow) public quests;

    event QuestCreated(uint256 questId, uint256 parentQuestId, address payer, address payee, uint256 amount, bytes32 scopeHash, ExecutionType executionType);
    event QuestFunded(uint256 questId, uint256 parentQuestId, address payer, address payee, uint256 amount, bytes32 scopeHash);
    event QuestSubmitted(uint256 questId, bytes32 evidenceHash);
    event QuestApproved(uint256 questId);
    event QuestDisputed(uint256 questId, uint256 disputeId);
    event QuestExecuted(uint256 questId, DecisionType decisionType, uint16 splitBps, uint256 payerAmount, uint256 payeeAmount);
    event QuestFinalized(uint256 questId, DecisionType decisionType);
    event QuestCancelled(uint256 questId);

    constructor(address admin, address usdcToken) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        usdc = IERC20(usdcToken);
    }

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    function setDisputeManager(address disputeManager_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        disputeManager = IQuestDisputeManager(disputeManager_);
    }

    function setCoopWallet(address coop) external onlyRole(DEFAULT_ADMIN_ROLE) {
        cooperativeWallet = coop;
    }

    function fundQuest(
        uint256 questId,
        uint256 parentQuestId,
        address payer,
        address payee,
        uint256 amount,
        bytes32 scopeHash,
        ExecutionType executionType
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused nonReentrant {
        require(questId != 0, "INVALID_ID");
        QuestEscrow storage q = quests[questId];
        require(q.status == QuestStatus.NONE, "INVALID_STATUS");
        if (executionType == ExecutionType.HUMAN) {
            require(amount > 0, "INVALID_AMOUNT");
        }
        require(scopeHash != bytes32(0), "INVALID_SCOPE");
        require(payer != address(0) && payee != address(0), "INVALID_ADDR");

        if (executionType == ExecutionType.HUMAN && amount > 0) {
            usdc.safeTransferFrom(payer, address(this), amount);
        }

        q.questId = questId;
        q.parentQuestId = parentQuestId;
        q.payer = payer;
        q.payee = payee;
        q.amount = amount;
        q.scopeHash = scopeHash;
        q.status = QuestStatus.FUNDED;
        q.fundedAt = uint64(block.timestamp);
        q.executed = false;
        q.decisionType = DecisionType.NONE;
        q.decisionSplitBps = 0;
        q.executionType = executionType;

        emit QuestCreated(questId, parentQuestId, payer, payee, amount, scopeHash, executionType);
        emit QuestFunded(questId, parentQuestId, payer, payee, amount, scopeHash);
    }

    function submitQuest(uint256 questId, bytes32 evidenceHash) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        QuestEscrow storage q = quests[questId];
        require(q.status == QuestStatus.FUNDED, "INVALID_STATUS");
        require(evidenceHash != bytes32(0), "INVALID_EVIDENCE");
        q.status = QuestStatus.SUBMITTED;
        emit QuestSubmitted(questId, evidenceHash);
    }

    function approveQuest(uint256 questId) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        QuestEscrow storage q = quests[questId];
        require(q.status == QuestStatus.FUNDED || q.status == QuestStatus.SUBMITTED, "INVALID_STATUS");
        q.status = QuestStatus.APPROVED;
        emit QuestApproved(questId);
    }

    function openDispute(
        uint256 questId,
        uint256 disputeId,
        bytes32 evidenceHashCreator,
        bytes32 evidenceHashWorker
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        QuestEscrow storage q = quests[questId];
        require(q.status == QuestStatus.FUNDED || q.status == QuestStatus.SUBMITTED || q.status == QuestStatus.APPROVED, "INVALID_STATUS");
        require(q.disputeId == 0, "DISPUTE_EXISTS");
        require(evidenceHashCreator != bytes32(0) || evidenceHashWorker != bytes32(0), "INVALID_EVIDENCE");
        q.status = QuestStatus.DISPUTED;
        q.disputeId = disputeId;
        emit QuestDisputed(questId, disputeId);
        if (address(disputeManager) != address(0)) {
            (bool ok, ) = address(disputeManager).call(
                abi.encodeWithSignature(
                    "createDispute(uint256,uint256,bytes32,bytes32)",
                    disputeId,
                    questId,
                    evidenceHashCreator,
                    evidenceHashWorker
                )
            );
            require(ok, "DISPUTE_CREATE_FAIL");
        }
    }

    function executeQuest(uint256 questId, DecisionType decisionType, uint16 splitBps) external onlyRole(OPERATOR_ROLE) whenNotPaused nonReentrant {
        QuestEscrow storage q = quests[questId];
        require(!q.executed, "ALREADY_EXECUTED");
        require(q.status == QuestStatus.APPROVED || q.status == QuestStatus.RESOLVED || q.status == QuestStatus.DISPUTED, "INVALID_STATUS");

        if (q.disputeId != 0) {
            require(address(disputeManager) != address(0), "NO_DISPUTE_MANAGER");
            (bool resolved, uint8 dmDecision, uint16 dmSplit) = disputeManager.getDecision(q.disputeId);
            require(resolved, "DISPUTE_NOT_RESOLVED");
            require(uint8(decisionType) == dmDecision, "DECISION_MISMATCH");
            if (decisionType == DecisionType.SPLIT) {
                require(splitBps == dmSplit, "SPLIT_MISMATCH");
            }
            q.status = QuestStatus.RESOLVED;
        } else {
            require(q.status == QuestStatus.APPROVED, "NOT_APPROVED");
            decisionType = DecisionType.SUCCESS;
        }

        uint256 payerAmount = 0;
        uint256 payeeAmount = 0;

        if (decisionType == DecisionType.SUCCESS) {
            payeeAmount = q.amount;
            usdc.safeTransfer(q.payee, payeeAmount);
        } else if (decisionType == DecisionType.FAIL) {
            payerAmount = q.amount;
            usdc.safeTransfer(q.payer, payerAmount);
        } else if (decisionType == DecisionType.SPLIT) {
            require(splitBps <= 10000, "INVALID_SPLIT");
            payeeAmount = (q.amount * splitBps) / 10000;
            payerAmount = q.amount - payeeAmount;
            usdc.safeTransfer(q.payee, payeeAmount);
            usdc.safeTransfer(q.payer, payerAmount);
        }

        q.executed = true;
        q.decisionType = decisionType;
        q.decisionSplitBps = splitBps;
        q.status = QuestStatus.EXECUTED;
        emit QuestExecuted(questId, decisionType, splitBps, payerAmount, payeeAmount);
        emit QuestFinalized(questId, decisionType);
    }

    function cancelQuest(uint256 questId) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        QuestEscrow storage q = quests[questId];
        require(q.status == QuestStatus.NONE, "INVALID_STATUS");
        q.status = QuestStatus.CANCELLED;
        emit QuestCancelled(questId);
    }
}
