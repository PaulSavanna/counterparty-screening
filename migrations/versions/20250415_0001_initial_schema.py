"""initial schema

Revision ID: 20250415_0001
Revises:
Create Date: 2025-04-15 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20250415_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "check_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="low"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("signals_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_check_results_company_name", "check_results", ["company_name"])
    op.create_index("ix_check_results_id", "check_results", ["id"])


def downgrade() -> None:
    op.drop_index("ix_check_results_id", table_name="check_results")
    op.drop_index("ix_check_results_company_name", table_name="check_results")
    op.drop_table("check_results")
