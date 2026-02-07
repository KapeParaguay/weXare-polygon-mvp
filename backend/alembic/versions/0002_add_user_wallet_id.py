"""add user wallet_id

Revision ID: 0002_add_user_wallet_id
Revises: 0001_init
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_user_wallet_id"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("wallet_id", sa.String(), nullable=True))
    op.create_index("ix_users_wallet_id", "users", ["wallet_id"], unique=True)


def downgrade():
    op.drop_index("ix_users_wallet_id", table_name="users")
    op.drop_column("users", "wallet_id")
