from typing import Callable
from dataclasses import dataclass


@dataclass
class SkillOutcome:
    status: str
    artifact_url: str | None
    notes: str | None = None


SkillHandler = Callable[[dict], SkillOutcome]

_REGISTRY: dict[str, SkillHandler] = {}


def register(name: str, handler: SkillHandler) -> None:
    _REGISTRY[name] = handler


def get(name: str) -> SkillHandler | None:
    return _REGISTRY.get(name)


def all_skills() -> list[str]:
    return list(_REGISTRY.keys())
