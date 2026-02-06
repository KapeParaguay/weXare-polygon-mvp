// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "openzeppelin-contracts/contracts/utils/Pausable.sol";
import "openzeppelin-contracts/contracts/access/AccessControl.sol";

contract QuestDisputeManager is AccessControl, Pausable {
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    enum DisputeStatus { NONE, OPEN, JUDGING, RESOLVED, EXECUTED }
    enum VoteType { NONE, SUCCESS, FAIL, SPLIT }

    struct Vote {
        VoteType voteType;
        uint16 splitBps;
        bytes32 commentHash;
        bool exists;
    }

    struct Dispute {
        uint256 disputeId;
        uint256 questId;
        DisputeStatus status;
        address[3] judges;
        uint8 votesCount;
        VoteType decision;
        uint16 splitBps;
        uint64 createdAt;
        uint64 resolvedAt;
        bool executed;
        bytes32 evidenceHashCreator;
        bytes32 evidenceHashWorker;
    }

    mapping(uint256 => Dispute) public disputes;
    mapping(uint256 => mapping(address => Vote)) public votes;

    event DisputeCreated(uint256 disputeId, uint256 questId, bytes32 evidenceCreator, bytes32 evidenceWorker);
    event DisputeOpened(uint256 disputeId, uint256 questId);
    event JudgesAssigned(uint256 disputeId, address judge1, address judge2, address judge3);
    event VoteSubmitted(uint256 disputeId, address judge, VoteType voteType, uint16 splitBps, bytes32 commentHash);
    event JudgeVoted(uint256 disputeId, address judge, VoteType voteType);
    event DisputeResolved(uint256 disputeId, VoteType decisionType, uint16 splitBps);
    event DisputeFinalized(uint256 disputeId, VoteType decisionType, uint16 splitBps);
    event DisputeExecuted(uint256 disputeId);

    address public escrowManager;

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    function setEscrowManager(address escrow) external onlyRole(DEFAULT_ADMIN_ROLE) {
        escrowManager = escrow;
    }

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    function createDispute(
        uint256 disputeId,
        uint256 questId,
        bytes32 evidenceHashCreator,
        bytes32 evidenceHashWorker
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        Dispute storage d = disputes[disputeId];
        require(disputeId != 0, "INVALID_ID");
        require(d.disputeId == 0, "EXISTS");
        require(questId != 0, "INVALID_QUEST");
        d.disputeId = disputeId;
        d.questId = questId;
        d.status = DisputeStatus.OPEN;
        d.evidenceHashCreator = evidenceHashCreator;
        d.evidenceHashWorker = evidenceHashWorker;
        d.createdAt = uint64(block.timestamp);
        emit DisputeCreated(disputeId, questId, evidenceHashCreator, evidenceHashWorker);
        emit DisputeOpened(disputeId, questId);
    }

    function assignJudges(uint256 disputeId, address judge1, address judge2, address judge3) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        Dispute storage d = disputes[disputeId];
        require(d.status == DisputeStatus.OPEN, "INVALID_STATUS");
        require(judge1 != address(0) && judge2 != address(0) && judge3 != address(0), "INVALID_JUDGE");
        require(judge1 != judge2 && judge1 != judge3 && judge2 != judge3, "DUP_JUDGE");
        if (escrowManager != address(0)) {
            (bool ok, bytes memory data) = escrowManager.staticcall(
                abi.encodeWithSignature("quests(uint256)", d.questId)
            );
            if (ok && data.length >= 32 * 4) {
                (, , address payer, address payee) = abi.decode(data, (uint256, uint256, address, address));
                require(judge1 != payer && judge1 != payee, "JUDGE_CONFLICT");
                require(judge2 != payer && judge2 != payee, "JUDGE_CONFLICT");
                require(judge3 != payer && judge3 != payee, "JUDGE_CONFLICT");
            }
        }
        d.judges = [judge1, judge2, judge3];
        d.status = DisputeStatus.JUDGING;
        emit JudgesAssigned(disputeId, judge1, judge2, judge3);
    }

    function submitVote(uint256 disputeId, VoteType voteType, uint16 splitBps, bytes32 commentHash) external whenNotPaused {
        Dispute storage d = disputes[disputeId];
        require(d.status == DisputeStatus.JUDGING, "INVALID_STATUS");
        require(_isJudge(d, msg.sender), "NOT_JUDGE");
        require(commentHash != bytes32(0), "COMMENT_REQUIRED");
        require(voteType != VoteType.NONE, "INVALID_VOTE");
        Vote storage v = votes[disputeId][msg.sender];
        require(!v.exists, "ALREADY_VOTED");

        if (voteType == VoteType.SPLIT) {
            require(splitBps > 0 && splitBps < 10000, "INVALID_SPLIT");
        }

        votes[disputeId][msg.sender] = Vote({
            voteType: voteType,
            splitBps: splitBps,
            commentHash: commentHash,
            exists: true
        });
        d.votesCount += 1;

        emit VoteSubmitted(disputeId, msg.sender, voteType, splitBps, commentHash);
        emit JudgeVoted(disputeId, msg.sender, voteType);

        _tryResolve(disputeId);
    }

    function markExecuted(uint256 disputeId) external onlyRole(OPERATOR_ROLE) {
        Dispute storage d = disputes[disputeId];
        require(d.status == DisputeStatus.RESOLVED, "INVALID_STATUS");
        require(!d.executed, "ALREADY_EXECUTED");
        d.executed = true;
        d.status = DisputeStatus.EXECUTED;
        emit DisputeExecuted(disputeId);
    }

    function finalizeAndExecute(uint256 disputeId) external onlyRole(OPERATOR_ROLE) whenNotPaused {
        Dispute storage d = disputes[disputeId];
        require(d.status == DisputeStatus.RESOLVED, "INVALID_STATUS");
        require(!d.executed, "ALREADY_EXECUTED");
        require(escrowManager != address(0), "NO_ESCROW");

        (bool ok, ) = escrowManager.call(
            abi.encodeWithSignature(
                "executeQuest(uint256,uint8,uint16)",
                d.questId,
                uint8(d.decision),
                d.splitBps
            )
        );
        require(ok, "ESCROW_EXEC_FAIL");

        d.executed = true;
        d.status = DisputeStatus.EXECUTED;
        emit DisputeExecuted(disputeId);
    }

    function getDecision(uint256 disputeId) external view returns (bool, VoteType, uint16) {
        Dispute storage d = disputes[disputeId];
        return (d.status == DisputeStatus.RESOLVED || d.status == DisputeStatus.EXECUTED, d.decision, d.splitBps);
    }

    function _isJudge(Dispute storage d, address a) internal view returns (bool) {
        return a == d.judges[0] || a == d.judges[1] || a == d.judges[2];
    }

    function _bucketSplit(uint16 splitBps) internal pure returns (uint16) {
        // Bucket to nearest 5% (500 bps)
        uint16 bucket = 500;
        return uint16((splitBps / bucket) * bucket);
    }

    function _tryResolve(uint256 disputeId) internal {
        Dispute storage d = disputes[disputeId];
        if (d.votesCount < 2 || d.status != DisputeStatus.JUDGING) {
            return;
        }

        Vote memory v1 = votes[disputeId][d.judges[0]];
        Vote memory v2 = votes[disputeId][d.judges[1]];
        Vote memory v3 = votes[disputeId][d.judges[2]];

        // Check pairwise majority
        if (v1.exists && v2.exists && _sameDecision(v1, v2)) {
            _resolve(disputeId, v1);
            return;
        }
        if (v1.exists && v3.exists && _sameDecision(v1, v3)) {
            _resolve(disputeId, v1);
            return;
        }
        if (v2.exists && v3.exists && _sameDecision(v2, v3)) {
            _resolve(disputeId, v2);
            return;
        }
    }

    function _sameDecision(Vote memory a, Vote memory b) internal pure returns (bool) {
        if (a.voteType != b.voteType) return false;
        if (a.voteType == VoteType.SPLIT) {
            return _bucketSplit(a.splitBps) == _bucketSplit(b.splitBps);
        }
        return true;
    }

    function _resolve(uint256 disputeId, Vote memory v) internal {
        Dispute storage d = disputes[disputeId];
        d.status = DisputeStatus.RESOLVED;
        d.decision = v.voteType;
        if (v.voteType == VoteType.SPLIT) {
            d.splitBps = _bucketSplit(v.splitBps);
        }
        d.resolvedAt = uint64(block.timestamp);
        emit DisputeResolved(disputeId, d.decision, d.splitBps);
        emit DisputeFinalized(disputeId, d.decision, d.splitBps);
    }
}
