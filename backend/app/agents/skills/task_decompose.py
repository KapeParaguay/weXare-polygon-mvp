from app.agents.skills.registry import SkillOutcome
from app.llm.selector import LLMSelector


def run(context: dict) -> SkillOutcome:
    llm = LLMSelector().get()
    if not llm:
        return SkillOutcome(status="failed", artifact_url=None, notes="No LLM provider available")
    prompt = context.get("prompt") or "Decompose the task into subtasks."
    resp = llm.generate(prompt)
    return SkillOutcome(status="success", artifact_url=None, notes=resp.text)
