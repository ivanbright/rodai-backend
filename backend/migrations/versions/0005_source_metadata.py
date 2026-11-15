"""Store source provenance for local benchmark sessions.

Revision ID: 0005_source_metadata
Revises: 0004_session_restart_recovery
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_source_metadata"
down_revision = "0004_session_restart_recovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("source_metadata", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("sources", "source_metadata")
