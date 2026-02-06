from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    name: str
    fn: Callable


@dataclass
class Agent:
    name: str
    capabilities: list[str]
    tools: list[Tool]


def create_project(*args, **kwargs):
    raise NotImplementedError


def create_proposal_version(*args, **kwargs):
    raise NotImplementedError


def lock_proposal(*args, **kwargs):
    raise NotImplementedError


def create_quest(*args, **kwargs):
    raise NotImplementedError


def set_scope_hash(*args, **kwargs):
    raise NotImplementedError


def calculate_budget(*args, **kwargs):
    raise NotImplementedError


def create_task(*args, **kwargs):
    raise NotImplementedError


def publish_task_to_feed(*args, **kwargs):
    raise NotImplementedError


def select_workers(*args, **kwargs):
    raise NotImplementedError


def issue_task_offers(*args, **kwargs):
    from app.services.orchestration import issue_wave
    return issue_wave(*args, **kwargs)


def send_email_offer(*args, **kwargs):
    raise NotImplementedError


def upload_evidence_metadata(*args, **kwargs):
    raise NotImplementedError


def open_dispute(*args, **kwargs):
    raise NotImplementedError


def create_judge_offers_wave(*args, **kwargs):
    raise NotImplementedError


def record_vote(*args, **kwargs):
    raise NotImplementedError


def resolve_dispute(*args, **kwargs):
    raise NotImplementedError


def call_protocol_contract(*args, **kwargs):
    raise NotImplementedError


def custodial_sign_and_send_tx(*args, **kwargs):
    raise NotImplementedError


TOOL_REGISTRY = [
    Tool("create_project", create_project),
    Tool("create_proposal_version", create_proposal_version),
    Tool("lock_proposal", lock_proposal),
    Tool("create_quest", create_quest),
    Tool("set_scope_hash", set_scope_hash),
    Tool("calculate_budget", calculate_budget),
    Tool("create_task", create_task),
    Tool("publish_task_to_feed", publish_task_to_feed),
    Tool("select_workers", select_workers),
    Tool("issue_task_offers", issue_task_offers),
    Tool("send_email_offer", send_email_offer),
    Tool("upload_evidence_metadata", upload_evidence_metadata),
    Tool("open_dispute", open_dispute),
    Tool("create_judge_offers_wave", create_judge_offers_wave),
    Tool("record_vote", record_vote),
    Tool("resolve_dispute", resolve_dispute),
    Tool("call_protocol_contract", call_protocol_contract),
    Tool("custodial_sign_and_send_tx", custodial_sign_and_send_tx),
]


PlannerAgent = Agent(
    name="PlannerAgent",
    capabilities=[
        "parse_creator_goal",
        "generate_quests",
        "define_acceptance_criteria_per_quest",
        "estimate_budget_with_buffer",
        "split_work_ai_human",
        "produce_proposal_object",
    ],
    tools=TOOL_REGISTRY,
)

OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    capabilities=[
        "create_task_list",
        "run_ai_subtasks",
        "publish_human_tasks",
        "prioritize_workers",
        "external_fallback",
        "compile_evidence_bundle",
        "move_to_review",
    ],
    tools=TOOL_REGISTRY,
)

QAAgent = Agent(
    name="QAAgent",
    capabilities=[
        "verify_acceptance_criteria",
        "verify_evidence_present",
        "flag_missing_items",
        "summarize_deliverables",
    ],
    tools=TOOL_REGISTRY,
)
