from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from rodai.config import Settings
from rodai.retention import register_artifact, sweep_expired_artifacts


@pytest.fixture
def retention_db(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'retention.sqlite'}")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE sources (id TEXT PRIMARY KEY)")
        connection.exec_driver_sql("CREATE TABLE sessions (id TEXT PRIMARY KEY, source_id TEXT)")
        connection.exec_driver_sql("CREATE TABLE events (id TEXT PRIMARY KEY, session_id TEXT)")
        connection.exec_driver_sql(
            "CREATE TABLE session_results (id TEXT PRIMARY KEY, session_id TEXT)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE retention_artifacts (id TEXT PRIMARY KEY, session_id TEXT, "
            "artifact_type TEXT, relative_path TEXT, expires_at DATETIME, created_at DATETIME, "
            "last_error TEXT)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE retention_audit (id TEXT PRIMARY KEY, artifact_id TEXT, "
            "artifact_type TEXT, expires_at DATETIME, attempted_at DATETIME, outcome TEXT, "
            "detail TEXT)"
        )
    yield engine, tmp_path
    engine.dispose()


def test_sweep_deletes_only_expired_allowed_artifacts_and_is_idempotent(retention_db) -> None:
    engine, root = retention_db
    now = datetime(2026, 11, 14, tzinfo=UTC)
    expired = root / "old.mp4"
    current = root / "current.mp4"
    expired.write_bytes(b"expired")
    current.write_bytes(b"current")
    register_artifact(
        engine,
        session_id="s1",
        artifact_type="upload",
        relative_path="old.mp4",
        retention_days=1,
        now=now - timedelta(days=2),
    )
    register_artifact(
        engine,
        session_id="s2",
        artifact_type="upload",
        relative_path="current.mp4",
        retention_days=1,
        now=now,
    )
    settings = Settings(data_dir=root)

    assert sweep_expired_artifacts(settings, engine, now=now) == {
        "deleted": 1,
        "failed": 0,
        "skipped": 0,
    }
    assert not expired.exists()
    assert current.read_bytes() == b"current"
    assert sweep_expired_artifacts(settings, engine, now=now) == {
        "deleted": 0,
        "failed": 0,
        "skipped": 0,
    }
    with engine.connect() as connection:
        assert connection.execute(text("SELECT outcome FROM retention_audit")).scalars().all() == [
            "deleted"
        ]


def test_sweep_retries_filesystem_failure_and_rejects_model_expiry(
    retention_db, monkeypatch
) -> None:
    engine, root = retention_db
    now = datetime(2026, 11, 14, tzinfo=UTC)
    artifact = root / "upload.mp4"
    artifact.write_bytes(b"retained")
    artifact_id = register_artifact(
        engine,
        session_id="s1",
        artifact_type="upload",
        relative_path="upload.mp4",
        retention_days=1,
        now=now - timedelta(days=2),
    )
    with pytest.raises(ValueError, match="cannot be registered"):
        register_artifact(
            engine,
            session_id="s1",
            artifact_type="model",
            relative_path="models/a.pt",
            retention_days=1,
            now=now - timedelta(days=2),
        )
    original_unlink = Path.unlink

    def fail_once(path: Path, *args, **kwargs):
        if path.name == "upload.mp4" and not getattr(fail_once, "failed", False):
            fail_once.failed = True
            raise PermissionError("locked")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_once)
    settings = Settings(data_dir=root)
    assert sweep_expired_artifacts(settings, engine, now=now)["failed"] == 1
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT id FROM retention_artifacts")).scalar_one()
            == artifact_id
        )
        assert connection.execute(
            text("SELECT outcome FROM retention_audit ORDER BY attempted_at")
        ).scalars().all() == ["failed"]
    assert sweep_expired_artifacts(settings, engine, now=now)["deleted"] == 1
    assert not artifact.exists()
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT outcome FROM retention_audit ORDER BY rowid")
        ).scalars().all() == ["failed", "deleted"]
