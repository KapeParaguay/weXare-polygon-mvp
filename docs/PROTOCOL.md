# WEXARE MVP PROTOCOL (Polygon · USDC · Quest Tree)

## 0) Objective
Guarantee on‑chain:
- USDC escrow for funded quests
- Immutable scope on funding (scopeHash)
- Disputes with 3 judges, majority 2/3
- Final execution: RELEASE / REFUND / SPLIT
- No double execution, no reentrancy, no invalid states
- Full events for audit/indexing

Everything else stays off‑chain (backend + Privy + cooperative).

## 1) MVP Decisions
- Chain: Polygon
- Asset: USDC (ERC‑20)
- Wallets: custodial (Privy), server‑side signing
- UX: Web2 only
- Escrow: per funded quest (parent/child)
- Disputes: 3 judges, majority 2/3
- Withdrawals: off‑chain only

## 2) Single Entity: Quest (parent/child tree)
- Root quest describes overall objective.
- Subquests replace milestones.
- Protocol operates on funded quests.
- `parentQuestId` is for traceability only.

## 3) Contracts
- `QuestEscrowManager.sol`
- `QuestDisputeManager.sol`
- `OperatorRegistry.sol` (AccessControl)

## 4) Roles & Permissions
- `DEFAULT_ADMIN_ROLE`: system owner
- `OPERATOR_ROLE`: backend/orchestrator

`QuestEscrowManager` and `QuestDisputeManager` grant `OPERATOR_ROLE` to each other to call cross‑contract methods.

## 5) Quest Status
`NONE → FUNDED → SUBMITTED → APPROVED → DISPUTED → RESOLVED → EXECUTED` (+ optional `CANCELLED` before funding)

## 6) Dispute Status
`NONE → OPEN → JUDGING → RESOLVED → EXECUTED`

## 7) Data Model
### QuestEscrow
- `questId`, `parentQuestId`
- `payer`, `payee`
- `amount`, `scopeHash`
- `status`, `disputeId`
- `fundedAt`, `executed`
- `decisionType`, `decisionSplitBps`
- `executionType` (HUMAN/AUTO metadata)

### Dispute
- `disputeId`, `questId`, `status`
- `judges[3]`, votes
- `decisionType`, `splitBps`
- `createdAt`, `resolvedAt`, `executed`

## 8) Core Functions
### Escrow Manager
- `fundQuest(questId, parentQuestId, payer, payee, amount, scopeHash, executionType)`
- `submitQuest(questId, evidenceHash)`
- `approveQuest(questId)`
- `openDispute(questId, disputeId, evidenceCreator, evidenceWorker)`
- `executeQuest(questId, decisionType, splitBps)`

### Dispute Manager
- `createDispute(disputeId, questId, evidenceCreator, evidenceWorker)`
- `assignJudges(disputeId, judge1, judge2, judge3)`
- `submitVote(disputeId, voteType, splitBps, commentHash)`
- `finalizeAndExecute(disputeId)`

## 9) Split Rule (MVP)
Split is accepted only if 2 judges vote SPLIT in the same bucket (e.g. 5% increments).

## 10) Events
- `QuestFunded`, `QuestSubmitted`, `QuestApproved`, `QuestDisputed`, `QuestExecuted`, `QuestCancelled`
- `DisputeCreated`, `JudgesAssigned`, `VoteSubmitted`, `DisputeResolved`, `DisputeExecuted`

## 11) Security
- ReentrancyGuard
- AccessControl
- Pausable
- Prevent double execution

## 12) What is NOT on‑chain
- Identity/KYC
- Reputation
- Agent orchestration
- Evidence storage

## 13) Tests (Foundry)
- fund → approve → release
- fund → dispute → 3 judges → majority → execute
- no double execute
- non‑judge cannot vote
- scope hash immutable
- parent/child isolation
