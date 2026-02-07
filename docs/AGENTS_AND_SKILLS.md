# Agents and Skills (MVP)

This document defines how agents, skills, and external tools are used in the WEXARE MVP.

The goal is to clearly separate:
- what is executed automatically by software,
- what requires human labor,
- and how both are coordinated without contaminating the protocol layer.

## 1. Fundamental Principle
Agents execute everything that can be objectively verified by software.  
Humans are involved only when verification or execution cannot be automated.

As a consequence:
- Automated execution is free and unlimited.
- Human execution is scarce, paid, and reputation-bearing.
- The protocol only enforces guarantees for human work.

## 2. Agent Types in the MVP
The MVP uses two logical agents.  
They may run as separate services or as modules within the backend.

### 2.1 Planner Agent
**Purpose:** Convert a creator’s goal into a structured execution plan.

The Planner Agent:
- receives a high-level goal from the creator,
- uses an LLM provider with fallback (OpenAI → OpenRouter),
- generates a tree of Quests (parent, children, deeper levels),
- assigns each Quest an execution type:
  - `AUTO` or `HUMAN`,
- defines acceptance criteria for each Quest,
- estimates human costs and funding requirements.

The Planner Agent:
- does not execute work,
- does not handle payments,
- produces deterministic, structured output (JSON).

### 2.2 Execution Agent (Task Router)
**Purpose:** Execute the plan and keep the system progressing.

The Execution Agent:
- iterates through child Quests,
- for `AUTO` Quests:
  - executes the appropriate skill via the SkillRunner,
- for `HUMAN` Quests:
  - selects and contacts eligible workers,
- enforces timeouts and retries,
- converts failed AUTO Quests into HUMAN Quests when necessary.

This agent ensures that no Quest blocks the overall execution.

## 3. AUTO vs HUMAN Quests
### 3.1 AUTO Quests
AUTO Quests:
- are executed by agent skills,
- must have software-verifiable outcomes,
- produce artifacts (text, documents, links, structured data),
- do not generate payments,
- do not affect reputation.

Possible outcomes:
- `SUCCESS`
- `NEEDS_HUMAN`
- `FAILED`

### 3.2 HUMAN Quests
HUMAN Quests:
- are assigned to workers,
- are funded via USDC escrow,
- require evidence submission,
- may enter dispute resolution,
- generate experience and reputation signals.

## 4. SkillRunner
The SkillRunner is a generic execution framework for AUTO Quests.

### 4.1 Skill Interface
Each skill receives:
- Quest context,
- acceptance criteria,
- execution constraints.

Each skill returns:
- execution status,
- an artifact (content or link),
- evidence references,
- optional notes.

Skills must be deterministic and time-bounded.

## 5. MVP Skills
The MVP intentionally limits the number of skills.

### 5.1 Writing Skill
- Drafts text deliverables.
- Produces markdown or plain text.
- Fallbacks to HUMAN when subjective approval is required.

### 5.2 Research Skill
- Performs web research.
- Produces summaries with sources.
- Uses external search APIs (e.g. Exa).

### 5.3 Document Generation Skill
- Generates shareable documents.
- Integrates with Google Docs via MCP.
- Produces a document link as evidence.

### 5.4 Email Skill
- Sends outreach or notification emails.
- Used for contacting external workers or stakeholders.
- Produces delivery metadata as evidence.

Optional notification-only skills (Slack/Discord) may be added but are non-critical.

## 6. External Tools and MCPs
Model Context Providers (MCPs) are used exclusively by agents and never by the protocol.

In the MVP:
- Google Docs MCP is used for artifact creation.
- Email MCP or SMTP is used for outreach.
- Slack/Discord MCP is optional and informational only.

Failure of an MCP must never block core execution.

## 7. External Human Sourcing
If no suitable worker exists within the protocol:
- external sources may be contacted,
- execution may proceed without immediate reputation,
- onboarding may be offered after completion.

External sourcing is a fallback, not a primary path.

## 8. What Is Explicitly Out of Scope
The MVP does not include:
- agent marketplaces,
- paid agents,
- on-chain agent reputation,
- permissionless agent execution,
- token incentives.

These may be explored after validation.

## 9. Design Rationale
This separation ensures:
- low-cost automation,
- reliable human guarantees,
- clean protocol boundaries,
- extensibility without redesign.

Agents evolve independently from the protocol.
