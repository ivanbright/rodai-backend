"""Persist video analysis settings and bounded restart recovery state.

Revision ID: 0004_session_restart_recovery
Revises: 0003_session_failure_details
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_session_restart_recovery"
down_revision = "0003_session_failure_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("analysis_fps", sa.Float(), nullable=True))
    op.add_column(
        "sessions",
        sa.Column("restart_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("sessions", "restart_count")
    op.drop_column("sessions", "analysis_fps")
