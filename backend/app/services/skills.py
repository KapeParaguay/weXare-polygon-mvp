from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class SkillResult:
    status: str
    artifact_url: str | None


def run_skill(skill_type: str, context: dict) -> SkillResult:
    # MVP stub: deterministic-ish
    if skill_type in {"writing", "docs_generate"}:
        return SkillResult(status="success", artifact_url="https://example.com/artifact")
    if skill_type == "research":
        return SkillResult(status="needs_human", artifact_url=None)
    return SkillResult(status="failed", artifact_url=None)
