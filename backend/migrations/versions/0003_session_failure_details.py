"""Persist a safe diagnostic message for failed video sessions.

Revision ID: 0003_session_failure_details
Revises: 0002_retention
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_session_failure_details"
down_revision = "0002_retention"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("error", sa.Text(), nullable=True))
    op.get_bind().execute(
        sa.text("UPDATE sessions SET error = :error WHERE status = 'failed' AND error IS NULL"),
        {
            "error": (
                "This session failed before detailed diagnostics were stored. "
                "Start a new video analysis to capture diagnostics if the problem repeats."
            )
        },
    )


def downgrade() -> None:
    op.drop_column("sessions", "error")
