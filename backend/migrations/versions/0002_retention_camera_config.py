"""Track expiring artifacts and effective camera settings.

Revision ID: 0002_retention
Revises: 0001_initial
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_retention"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("camera_config", sa.JSON(), nullable=True))
    op.create_table(
        "retention_artifacts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("relative_path", sa.String(length=1024), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.String(length=512), nullable=True),
    )
    op.create_table(
        "retention_audit",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("detail", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("retention_audit")
    op.drop_table("retention_artifacts")
    op.drop_column("sessions", "camera_config")
