# ARCHITECTURE

High-level architecture for the WEXARE MVP.

## Components
- **Frontend**: Next.js (App Router), Web2 UX, no blockchain visible.
- **Backend**: FastAPI + SQLAlchemy + Alembic, source of truth for state.
- **Protocol**: Solidity contracts on Polygon (USDC escrow + disputes).
- **Infra**: Docker Compose, Makefile, CI.

## Data Flow
1. Creator submits a goal.
2. PlannerAgent generates a quest tree and budget.
3. Creator funds a quest (USDC on-chain).
4. OrchestratorAgent routes AUTO vs HUMAN.
5. Workers submit evidence; creator approves or disputes.
6. Disputes resolve by 3 judges (majority).

## Separation of Concerns
- Protocol: escrow + disputes only.
- Backend: orchestration, wallets, evidence, reputation, LLM provider abstraction.
- Background polling (indexer) runs inside the backend process (no separate worker infra).
- Frontend: Web2 UX.
