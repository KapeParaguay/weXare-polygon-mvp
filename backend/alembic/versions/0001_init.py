"""init

Revision ID: 0001
Revises:
Create Date: 2026-02-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), unique=True, index=True),
        sa.Column("wallet_address", sa.String(), unique=True, index=True, nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("roles", sa.String(), nullable=False),
    )
    op.create_table(
        "worker_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("pricing", sa.Float(), nullable=False),
        sa.Column("scores", sa.Float(), nullable=False),
        sa.Column("active_task_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "judge_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("judge_score", sa.Float(), nullable=False),
        sa.Column("acceptance_rate", sa.Float(), nullable=False),
        sa.Column("cooldown", sa.Integer(), nullable=False),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("creator_id", sa.String(), index=True),
        sa.Column("title", sa.String()),
        sa.Column("description", sa.String()),
    )
    op.create_table(
        "proposals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), index=True),
        sa.Column("version", sa.Integer()),
        sa.Column("locked", sa.Boolean()),
        sa.Column("data", postgresql.JSONB()),
    )
    op.create_table(
        "quests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), index=True),
        sa.Column("parent_quest_id", sa.Integer(), nullable=True),
        sa.Column("index", sa.Integer()),
        sa.Column("scope_hash", sa.String()),
        sa.Column("budget", sa.Float()),
        sa.Column("status", sa.String()),
        sa.Column("funded_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("type", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("assigned_user_id", sa.String(), nullable=True),
    )
    op.create_table(
        "task_declines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), index=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("declined_at", sa.DateTime()),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.String(), index=True),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("quest_id", sa.Integer(), nullable=True),
        sa.Column("url", sa.String()),
        sa.Column("type", sa.String()),
    )
    op.create_table(
        "disputes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String()),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("opened_by", sa.String()),
        sa.Column("reason", sa.String()),
        sa.Column("evidence", sa.String()),
    )
    op.create_table(
        "judge_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dispute_id", sa.Integer(), index=True),
        sa.Column("judge_user_id", sa.String(), index=True),
        sa.Column("status", sa.String()),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "judge_votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dispute_id", sa.Integer(), index=True),
        sa.Column("judge_user_id", sa.String(), index=True),
        sa.Column("vote", sa.String()),
        sa.Column("split", sa.Integer()),
        sa.Column("comment", sa.String()),
    )
    op.create_table(
        "escrow_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("kind", sa.String()),
        sa.Column("onchain_tx", sa.String()),
        sa.Column("amount", sa.Float()),
        sa.Column("status", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("creator_id", sa.String(), index=True),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("amount", sa.Float()),
        sa.Column("fee", sa.Float()),
        sa.Column("status", sa.String()),
        sa.Column("provider", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "withdrawals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("amount", sa.Float()),
        sa.Column("method", sa.String()),
        sa.Column("destination", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("status", sa.String()),
        sa.Column("coop_tx", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "experience_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("role", sa.String()),
        sa.Column("outcome", sa.String()),
        sa.Column("was_disputed", sa.Boolean()),
        sa.Column("dispute_result", sa.String(), nullable=True),
        sa.Column("executor_type", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "indexer_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(), unique=True, index=True),
        sa.Column("value", sa.String()),
    )
    op.create_table(
        "reputation_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("role", sa.String()),
        sa.Column("previous_score", sa.Float()),
        sa.Column("new_score", sa.Float()),
        sa.Column("formula_version", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "task_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), index=True),
        sa.Column("worker_id", sa.String(), index=True),
        sa.Column("status", sa.String()),
        sa.Column("expires_at", sa.DateTime()),
    )
    op.create_table(
        "skill_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quest_id", sa.Integer(), index=True),
        sa.Column("skill_type", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("artifact_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.String()),
        sa.Column("action", sa.String()),
        sa.Column("details", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade():
    op.drop_table("audit_log")
    op.drop_table("indexer_state")
    op.drop_table("escrow_ledger")
    op.drop_table("judge_votes")
    op.drop_table("judge_offers")
    op.drop_table("disputes")
    op.drop_table("evidence")
    op.drop_table("task_declines")
    op.drop_table("tasks")
    op.drop_table("skill_runs")
    op.drop_table("task_offers")
    op.drop_table("reputation_logs")
    op.drop_table("experience_records")
    op.drop_table("withdrawals")
    op.drop_table("payments")
    op.drop_table("quests")
    op.drop_table("proposals")
    op.drop_table("projects")
    op.drop_table("judge_profiles")
    op.drop_table("worker_profiles")
    op.drop_table("users")
