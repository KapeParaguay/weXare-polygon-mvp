# WEXARE MVP

WEXARE MVP: agent-orchestrated work platform with quest-based escrow, human+AI execution, and dispute resolution, with Web2 UX.

## What this MVP is about
WEXARE is not a marketplace of humans, and it is not just another AI agent platform.

WEXARE is a hybrid work orchestration system where software agents execute everything that can be objectively verified, and humans are involved only when automation is insufficient.

A creator describes a goal. The system converts that goal into a structured Quest tree with clear acceptance criteria. Each Quest is classified as either:
- `AUTO` — executed by agents using deterministic skills, or
- `HUMAN` — executed by humans and paid via escrow.

This separation is the core of the product.

## Why this is different (Blue Ocean)
Most existing solutions fall into one of two categories:
- Human marketplaces: humans first, coordination overhead everywhere, limited automation.
- Agent platforms: agents execute tasks but lack a reliable path for human fallback, payments, and dispute resolution.

WEXARE sits in a different space:
> Agents are the default executors. Humans are the exception — but when involved, they are coordinated, paid, and arbitrated with guarantees.

This changes the cost structure, execution speed, and reliability of outcomes.

## Core design principle
> If a task can be verified by software, it should never require human labor.

Only tasks that require judgment, expertise, or non-deterministic validation are delegated to humans.
As a result:
- Creators pay only for irreducibly human work.
- Agents eliminate entire categories of operational cost.
- The system scales without coordinators or recruiters.

## Payments and guarantees
Human work is paid through USDC escrow on-chain (Polygon for the MVP), with:
- Quest-level releases (modeled as Quest nodes),
- dispute resolution by three independent judges,
- majority-based finalization.

Despite this, the UX is Web2-first: no seed phrases, no gas prompts, no blockchain concepts exposed to the user.
Blockchain exists only to enforce guarantees, not to burden users.

## Why this MVP looks simpler than the final protocol
This MVP deliberately prioritizes fast iteration, real user flows, and incentive validation.

Several components are centralized or operator-based by design, not as shortcuts.
They will be decentralized only after the model is validated in practice.

## What this MVP validates
This MVP is built to validate:
- automated planning → hybrid execution,
- agent-first workflows with human fallback,
- escrow-backed payments for human work,
- dispute resolution with minimal overhead,
- the economic advantage of agent-heavy execution.

It does not attempt to solve governance, tokenomics, or full decentralization yet.

## Experience registry and reputation (differentiator)
Every HUMAN Quest produces an **ExperienceRecord** for each participant (worker/judge/creator).  
These records are objective, event-based, and tied to real outcomes (success, dispute, split).

This creates a **portable, verifiable track record** across the platform that is not based on subjective reviews.
Reputation is derived from these records per role (worker/judge/creator), not from ratings.

This is a key differentiator: the protocol does not just coordinate work — it **creates auditable proof of human execution**.

## Summary in one sentence
WEXARE coordinates agents and humans as a single execution system, where humans are paid only when automation is not enough and every human quest creates verifiable experience and reputation.

## Why Polygon (MVP)
Polygon is used **only** for the MVP due to iteration speed, mature tooling, and low costs. The final protocol will migrate to Solana later.

## Web2 UX
- Email magic link login
- Custodial wallets (Privy)
- Platform pays gas
- Users see: “Available funds”, “Fund quest”, “Approve”, “Dispute”, “Vote”

## Stablecoin
- **USDC on Polygon** (single currency for MVP)

## Withdrawals
- **Enabled** but **only to a verified cooperative wallet**
- Cooperative pays users via bank off-chain

## On‑ramp (MVP)
- MoonPay for creators
- States: INITIATED, PAID_PENDING_USDC, USDC_CONFIRMED, FAILED
- Quest funding only after `USDC_CONFIRMED`

## Architecture
- `frontend/` Next.js App Router + Tailwind + TanStack Query
- `backend/` FastAPI + SQLAlchemy + Alembic
- `protocol/` Solidity + Foundry
- `infra/` Docker Compose

## Protocol (MVP)
- USDC escrow per Quest (quest tree: parent/child)
- Disputes with 3 judges, majority 2/3 on-chain
- Decisions: release, refund, split

## Agents
- PlannerAgent
- OrchestratorAgent
- QAAgent

See `docs/AGENTS.md`, `docs/AGENTS_AND_SKILLS.md`, and `docs/ARCHITECTURE.md`.

## Commands
- `make dev`
- `make test`
- `make deploy`

## Install dependencies (first time)
Frontend:
```bash
cd frontend
npm install
```

Backend:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Protocol:
```bash
cd protocol
forge install
```

## Environment variables (minimum)
Backend (`backend/.env`)
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PRIVY_APP_ID`
- `PRIVY_APP_SECRET`
- `USDC_TOKEN_ADDRESS`
- `ESCROW_MANAGER_ADDRESS`
- `DISPUTE_MANAGER_ADDRESS`
- `COOPERATIVE_WITHDRAWAL_ADDRESS`
- `RPC_URL`
- `INDEXER_POLL_SEC`
- `INDEXER_START_BLOCK`

Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Protocol (`protocol/.env`)
- `AMOY_RPC_URL`
- `DEPLOYER_PRIVATE_KEY`
- `ADMIN_ADDRESS`
- `USDC_ADDRESS`
- `COOP_WALLET_ADDRESS`

## End‑to‑end local MVP (quick test)
1. Start local stack: `make dev`.
2. Backend migrations/seed if applicable.
3. Open frontend at `http://localhost:3000`.
4. Use any Authorization header in dev (auth is stubbed).
5. Creator: create project and generate proposal.
6. Fund: initiate payment and confirm `USDC_CONFIRMED`.
7. Fund a quest from `/creator/fund`.
8. Worker: accept task and submit evidence.
9. Creator: approve or dispute.
10. Judge: accept offer and vote.
11. Check balances and withdrawals in `/wallet/withdraw`.

### E2E real with indexer (minimum)
Prereqs: contracts deployed on Anvil/local + env vars set.

**Terminal A**
```bash
cd protocol
anvil
```

**Terminal B**
```bash
cd protocol
FOUNDRY_DISABLE_SIGS=1 forge script script/DeployLocal.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
```

Export addresses:
```bash
export RPC_URL=http://127.0.0.1:8545
export ESCROW_MANAGER_ADDRESS=0x...
export DISPUTE_MANAGER_ADDRESS=0x...
export USDC_TOKEN_ADDRESS=0x...

cd backend
RUN_E2E=1 pytest -q tests/test_e2e_flow.py
```

## Production guide (MVP)
1. Managed Postgres (Supabase or equivalent) + `DATABASE_URL`.
2. Secrets in vault/KMS (no `.env` in prod).
3. Deploy backend + background workers.
4. Configure `RPC_URL`, `USDC_TOKEN_ADDRESS`, `ESCROW_MANAGER_ADDRESS`, `DISPUTE_MANAGER_ADDRESS`.
5. Set `COOPERATIVE_WITHDRAWAL_ADDRESS` (fixed wallet).
6. Enable Supabase Auth (magic link) and replace auth stub.
7. Configure domains + CORS.
8. Run migrations: `alembic upgrade head`.
9. Run indexer as a service and monitor it.
10. Centralized logs and alerts.

## Protocol testing
1. Local tests:
   - `cd protocol`
   - `FOUNDRY_DISABLE_SIGS=1 forge test -vvv`
2. Fork tests:
   - `anvil --fork-url https://polygon-rpc.com --chain-id 31337`
   - `FORK=true FOUNDRY_DISABLE_SIGS=1 forge test --match-path test/ForkUSDC.t.sol -vvv --rpc-url http://127.0.0.1:8545`
3. Amoy:
   - `source .env`
   - `FOUNDRY_DISABLE_SIGS=1 forge script script/Deploy.s.sol --rpc-url $AMOY_RPC_URL --private-key $DEPLOYER_PRIVATE_KEY --broadcast`

## Indexer guide
Run:
```bash
cd backend
python -m app.workers.indexer
```

Key envs: `RPC_URL`, `ESCROW_MANAGER_ADDRESS`, `DISPUTE_MANAGER_ADDRESS`, `INDEXER_POLL_SEC`, `INDEXER_START_BLOCK`.

Backfill:
- Set `INDEXER_START_BLOCK` to a prior block.
- Reset `indexer_state.last_block`.
- Restart the indexer.

## Pending for production
1. **Auth real** (Supabase magic link)
2. **Indexer ops** (monitoring + alerts)
3. **Balance reconciliation** (wallet_address mapping for all users)
4. **E2E tests** for full backend flow
5. **CI green** (`make test`)

## Pending integrations (Agents + Skills + MCPs)
- Email MCP/SMTP (SendGrid/SES/Mailgun)
- Google Docs MCP (Docs API)
- EXA / external human providers
- Planner with LLM (currently heuristic)
- Async agent runtime (RQ/Celery)

## Security (MVP)
- Custodial keys server‑side only
- Backend signs and pays gas
- Contracts use AccessControl + ReentrancyGuard

> Privy costs: billed to the platform (SaaS). Costs are covered via buffers and not shown to end users.
