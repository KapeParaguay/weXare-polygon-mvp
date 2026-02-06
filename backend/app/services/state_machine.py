"""Pure state machine rules for MVP (unit-testable)."""

MILESTONE_STATUSES = {
    "DRAFT",
    "FUNDED",
    "REVIEW",
    "APPROVED",
    "DISPUTE",
    "RESOLVED",
}


class StateError(Exception):
    pass


def can_fund(current_status: str) -> bool:
    return current_status in {"DRAFT"}


def can_submit_task(task_status: str) -> bool:
    return task_status in {"ACTIVE"}


def can_move_to_review(quest_status: str) -> bool:
    return quest_status == "FUNDED"


def can_approve(quest_status: str) -> bool:
    return quest_status == "REVIEW"


def can_dispute(quest_status: str) -> bool:
    return quest_status in {"REVIEW", "FUNDED"}


def ensure(condition: bool, message: str):
    if not condition:
        raise StateError(message)
