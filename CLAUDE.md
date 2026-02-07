# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

WEXARE MVP — an agent-orchestrated hybrid work platform with quest-based escrow, human+AI execution, and dispute resolution. Agents handle automatable work; humans are paid (USDC escrow on Polygon) only when automation is insufficient. Spanish-language UI.

## Monorepo Layout

- **frontend/** — Next.js 14 App Router, TypeScript, Tailwind, TanStack Query
- **backend/** — FastAPI (Python 3.11), SQLAlchemy, Alembic, Postgres
- **protocol/** — Solidity 0.8.24, Foundry (forge/anvil), OpenZeppelin
- **infra/** — Docker Compose (Postgres, Anvil, Mailhog, backend, frontend)
- **docs/** — 25 design docs covering architecture, protocol, agents, disputes, etc.

## Commands

### Full Stack
```bash
make dev          # docker compose up (Postgres, Anvil, Mailhog, backend, frontend)
make test         # runs all three test suites sequentially
```

### Frontend (from frontend/)
```bash
npm run dev       # next dev (port 3000)
npm run build     # next build
npm test          # playwright test (all E2E specs)
npx playwright test tests/flows.spec.ts   # single test file
```

### Backend (from backend/)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000   # run server
pytest                                               # all unit tests
pytest tests/test_state_machine.py                   # single test file
pytest tests/test_state_machine.py::test_name -v     # single test
alembic upgrade head                                 # run migrations
RUN_E2E=1 pytest -q tests/test_e2e_flow.py           # E2E (needs Anvil + deployed contracts)
RUN_INTEGRATION=1 pytest                              # integration tests (gated)
python -m app.workers.indexer                         # blockchain event indexer
```

### Protocol (from protocol/)
```bash
FOUNDRY_DISABLE_SIGS=1 forge test -vvv                # run all tests
FOUNDRY_DISABLE_SIGS=1 forge script script/DeployLocal.s.sol --rpc-url http://127.0.0.1:8545 --broadcast  # local deploy
FORK=true FOUNDRY_DISABLE_SIGS=1 forge test --match-path test/ForkUSDC.t.sol -vvv --rpc-url http://127.0.0.1:8545  # fork tests
```

## Architecture

### Quest State Machine
`backend/app/services/state_machine.py` — Pure functions governing quest lifecycle:
DRAFT → FUNDED → REVIEW → APPROVED → (done) or DISPUTE → RESOLVED → (done).
All state transitions are guarded here; always use these functions rather than mutating quest status directly.

### AUTO/HUMAN Task Routing
`backend/app/services/task_router.py` — When a quest task is created, the router first attempts an agent skill (`services/skills.py`). If the skill fails or is unsupported, it creates a HUMAN task and triggers worker offer waves via `services/orchestration.py`.

### Escrow Flow (On-chain ↔ Off-chain)
1. Creator funds quest → `QuestEscrowManager.sol` holds USDC
2. `backend/app/workers/indexer.py` polls chain events, syncs status to Postgres
3. Creator approves (release to worker) or disputes (3-judge panel)
4. `services/ledger.py` mirrors on-chain escrow as a custodial ledger (CREDIT, FUND, RELEASE, REFUND, SPLIT)

### Dispute Resolution
`QuestDisputeManager.sol` + `backend/app/services/judges.py` — 3-judge quorum, 2/3 majority. Decisions: SUCCESS (pay worker), FAIL (refund creator), SPLIT (basis points bucketed to nearest 5%). Judge offers are issued in waves with SLA tracking.

### Agent System
`backend/app/agents/registry.py` — Three agents (PlannerAgent, OrchestratorAgent, QAAgent) with tool registries. Most tool functions are stubs (`NotImplementedError`) in MVP. No real LLM integration yet; Planner uses heuristics.

### Backend API Structure
`backend/app/api/router.py` aggregates sub-routers: `creator`, `worker`, `judge`, `users`, `external`, `reputation`, `skills`. Auth is stubbed (any Bearer token returns a hardcoded user via `services/auth.py`).

### Database
SQLAlchemy sync sessions with `DeclarativeBase` pattern. 22 models in `backend/app/models/`. Session obtained via `get_db()` FastAPI dependency. Alembic migrations in `backend/alembic/` (single revision `0001_init`).

### Frontend API Layer
`frontend/lib/api.ts` — Thin fetch wrapper using `NEXT_PUBLIC_API_URL`. Auth header is hardcoded `Bearer mock`. Zod validation schemas in `frontend/lib/validators.ts`.

### Reputation & Experience
ELO-style reputation per role (worker/judge/creator) in `services/reputation.py` — +10 success, -10 fail, +2 split, base 1000. `services/experience.py` creates ExperienceRecords per quest completion.

## Testing

- **Backend**: pytest with in-memory SQLite. `conftest.py` overrides `get_db` and `get_current_user` dependencies. E2E tests gated behind `RUN_E2E=1`.
- **Frontend**: Playwright E2E specs in `frontend/tests/`. Config starts Next.js dev server automatically.
- **Protocol**: Foundry tests including fuzz tests. Always use `FOUNDRY_DISABLE_SIGS=1`.

## Key Environment Variables

- **Backend**: `DATABASE_URL`, `USDC_TOKEN_ADDRESS`, `ESCROW_MANAGER_ADDRESS`, `DISPUTE_MANAGER_ADDRESS`, `COOPERATIVE_WITHDRAWAL_ADDRESS`, `RPC_URL`
- **Frontend**: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Protocol**: `AMOY_RPC_URL`, `DEPLOYER_PRIVATE_KEY`, `ADMIN_ADDRESS`, `USDC_ADDRESS`, `COOP_WALLET_ADDRESS`

## MVP Stubs (not yet real)

Auth (hardcoded user), Privy wallet (deterministic hashes), MoonPay on-ramp, agent LLM calls, skills runner (hardcoded results), external human sources, async task queue (RQ/Celery not wired).
