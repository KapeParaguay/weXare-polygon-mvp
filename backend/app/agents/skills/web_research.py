from app.agents.skills.registry import SkillOutcome


def run(context: dict) -> SkillOutcome:
    # MVP stub for research
    return SkillOutcome(status="needs_human", artifact_url=None, notes="Research requires human verification")
