from dataclasses import dataclass
from app.agents.skills.registry import register, get as get_skill, SkillOutcome
from app.agents.skills import web_research, doc_write, task_decompose


@dataclass
class SkillResult:
    status: str
    artifact_url: str | None
    notes: str | None = None


def run_skill(skill_type: str, context: dict) -> SkillResult:
    # Registry setup (idempotent)
    register("writing", doc_write.run)
    register("docs_generate", doc_write.run)
    register("research", web_research.run)
    register("task_decompose", task_decompose.run)

    handler = get_skill(skill_type)
    if not handler:
        return SkillResult(status="failed", artifact_url=None, notes="Skill not found")
    outcome: SkillOutcome = handler(context)
    return SkillResult(status=outcome.status, artifact_url=outcome.artifact_url, notes=outcome.notes)
