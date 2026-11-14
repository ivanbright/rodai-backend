"""Auditable, retryable expiry for server-owned session artifacts."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import Engine, text

from rodai.config import Settings

logger = logging.getLogger("rodai.retention")
EXPIRABLE_TYPES = frozenset({"upload", "result", "export", "session"})


def register_artifact(
    engine: Engine,
    *,
    session_id: str,
    artifact_type: str,
    relative_path: str | None,
    retention_days: int,
    now: datetime | None = None,
) -> str:
    if artifact_type not in EXPIRABLE_TYPES:
        raise ValueError("Model and checkpoint artifacts cannot be registered for expiry.")
    created = now or datetime.now(UTC)
    artifact_id = str(uuid4())
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO retention_artifacts "
                "(id, session_id, artifact_type, relative_path, expires_at, created_at) "
                "VALUES (:id, :session_id, :type, :path, :expires, :created)"
            ),
            {
                "id": artifact_id,
                "session_id": session_id,
                "type": artifact_type,
                "path": relative_path,
                "expires": created + timedelta(days=retention_days),
                "created": created,
            },
        )
    return artifact_id


def sweep_expired_artifacts(
    settings: Settings,
    engine: Engine,
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """Remove expired allowed artifact classes; retain failed rows for retry."""
    current = now or datetime.now(UTC)
    counts = {"deleted": 0, "failed": 0, "skipped": 0}
    with engine.connect() as connection:
        rows = (
            connection.execute(
                text(
                    "SELECT id, session_id, artifact_type, relative_path, expires_at "
                    "FROM retention_artifacts "
                    "WHERE expires_at <= :now ORDER BY expires_at"
                ),
                {"now": current},
            )
            .mappings()
            .all()
        )
    root = settings.data_dir.resolve()
    for row in rows:
        artifact_id = str(row["id"])
        kind = str(row["artifact_type"])
        session_id = str(row["session_id"] or "")
        outcome = "deleted"
        detail = None
        try:
            if kind not in EXPIRABLE_TYPES:
                outcome, detail = "skipped", "Protected artifact type"
            else:
                relative = row["relative_path"]
                if relative:
                    target = (root / str(relative)).resolve()
                    if root not in target.parents:
                        raise ValueError("Artifact path escapes the configured data directory")
                    target.unlink(missing_ok=True)
                with engine.begin() as connection:
                    connection.execute(
                        text("DELETE FROM retention_artifacts WHERE id=:id"), {"id": artifact_id}
                    )
                    if kind == "result" and session_id:
                        connection.execute(
                            text("DELETE FROM session_results WHERE session_id=:id"),
                            {"id": session_id},
                        )
                    if kind == "session" and session_id:
                        connection.execute(
                            text("DELETE FROM events WHERE session_id=:id"), {"id": session_id}
                        )
                        connection.execute(
                            text("DELETE FROM session_results WHERE session_id=:id"),
                            {"id": session_id},
                        )
                        session = connection.execute(
                            text("SELECT source_id FROM sessions WHERE id=:id"), {"id": session_id}
                        ).first()
                        connection.execute(
                            text("DELETE FROM sessions WHERE id=:id"), {"id": session_id}
                        )
                        if session and session[0]:
                            connection.execute(
                                text("DELETE FROM sources WHERE id=:id"), {"id": session[0]}
                            )
        except Exception as exc:
            outcome = "failed"
            detail = type(exc).__name__ + ": " + str(exc)[:400]
            counts["failed"] += 1
            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE retention_artifacts SET last_error=:error WHERE id=:id"),
                    {"id": artifact_id, "error": detail},
                )
            logger.exception("Retention deletion failed artifact_id=%s type=%s", artifact_id, kind)
        else:
            if outcome == "deleted":
                counts["deleted"] += 1
            else:
                counts["skipped"] += 1
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO retention_audit "
                    "(id, artifact_id, artifact_type, expires_at, attempted_at, outcome, detail) "
                    "VALUES (:id,:artifact,:type,:expires,:at,:outcome,:detail)"
                ),
                {
                    "id": str(uuid4()),
                    "artifact": artifact_id,
                    "type": kind,
                    "expires": row["expires_at"],
                    "at": current,
                    "outcome": outcome,
                    "detail": detail,
                },
            )
    return counts


def retention_status(engine: Engine) -> dict[str, object]:
    try:
        with engine.connect() as connection:
            failed = connection.execute(
                text("SELECT COUNT(*) FROM retention_artifacts WHERE last_error IS NOT NULL")
            ).scalar_one()
        return {"status": "available", "failed_deletions": int(failed)}
    except Exception as exc:
        return {"status": "unavailable", "failed_deletions": None, "error_type": type(exc).__name__}
