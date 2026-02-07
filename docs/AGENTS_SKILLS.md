# Agents + Skills (MVP)

This MVP uses:
- **PlannerAgent** (LLM-backed) to generate quest trees and costs.
- **Execution Agent (Task Router)** to run AUTO skills or assign HUMAN tasks.

Skills are minimal and deterministic:
- `writing`
- `docs_generate`
- `research`
- `task_decompose`

AUTO quests never create reputation or payments.
HUMAN quests are escrowed and reputation-bearing.
