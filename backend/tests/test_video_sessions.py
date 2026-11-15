import json
import threading
import time
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from rodai.config import Settings
from rodai.sessions import (
    SessionControl,
    SessionRegistry,
    make_sessions_router,
    recover_interrupted_sessions,
)
from rodai.video_pipeline import process_video


@pytest.fixture
def session_client(tmp_path: Path) -> tuple[TestClient, Path]:
    engine = create_engine(f"sqlite:///{tmp_path / 'sessions.sqlite'}")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE sources (id VARCHAR(36) PRIMARY KEY, source_type VARCHAR(32), "
            "source_metadata TEXT, created_at DATETIME NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY, source_id VARCHAR(36), "
            "status VARCHAR(32) NOT NULL, created_at DATETIME NOT NULL, ended_at DATETIME, "
            "camera_config JSON, error TEXT, analysis_fps FLOAT, "
            "restart_count INTEGER NOT NULL DEFAULT 0)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE session_results (id VARCHAR(36) PRIMARY KEY, session_id VARCHAR(36), "
            "result_path VARCHAR(1024), schema_version VARCHAR(32), created_at DATETIME)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE retention_artifacts (id VARCHAR(36) PRIMARY KEY, session_id VARCHAR(36), "
            "artifact_type VARCHAR(32), relative_path VARCHAR(1024), expires_at DATETIME, "
            "created_at DATETIME, last_error VARCHAR(512))"
        )
        connection.exec_driver_sql(
            "CREATE TABLE retention_audit (id VARCHAR(36) PRIMARY KEY, artifact_id VARCHAR(36), "
            "artifact_type VARCHAR(32), expires_at DATETIME, attempted_at DATETIME, "
            "outcome VARCHAR(32), "
            "detail VARCHAR(512))"
        )
        connection.exec_driver_sql(
            "CREATE TABLE events (id VARCHAR(36) PRIMARY KEY, session_id VARCHAR(36), "
            "category VARCHAR(64), evidence_level VARCHAR(32), occurred_at DATETIME)"
        )
    app = FastAPI()
    app.include_router(make_sessions_router(Settings(data_dir=tmp_path), engine))
    with TestClient(app) as client:
        yield client, tmp_path
    engine.dispose()


def _make_test_video(path: Path) -> bytes:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 5.0, (64, 48))
    if not writer.isOpened():
        pytest.skip("This OpenCV build has no MJPG test-video encoder.")
    for value in (20, 80, 140):
        writer.write(np.full((48, 64, 3), value, dtype=np.uint8))
    writer.release()
    return path.read_bytes()


def _wait_for_session(client: TestClient, session_id: str) -> dict[str, object]:
    for _ in range(100):
        session = client.get(f"/api/v1/sessions/{session_id}").json()
        if session["status"] in {"completed", "failed"}:
            return session
        time.sleep(0.01)
    pytest.fail("Video session did not finish within one second.")


def test_video_upload_echoes_every_decoded_frame_and_can_be_deleted(
    session_client: tuple[TestClient, Path],
) -> None:
    client, data_dir = session_client
    video_bytes = _make_test_video(data_dir / "sample.avi")

    response = client.post(
        "/api/v1/sessions/video?filename=sample.avi",
        content=video_bytes,
        headers={"content-type": "video/x-msvideo"},
    )

    assert response.status_code == 202
    session = _wait_for_session(client, response.json()["id"])
    assert session["status"] == "completed"
    assert session["processed_frames"] == 3
    assert session["metadata"]["width"] == 64
    assert session["metadata"]["height"] == 48

    result = client.get(session["result_url"])
    records = [json.loads(line) for line in result.text.splitlines()]
    frames = [record for record in records if record["type"] == "frame"]
    assert [frame["frame_id"] for frame in frames] == [0, 1, 2]
    assert all(frame["detections"] == [] for frame in frames)
    assert records[-1]["type"] == "summary"
    assert records[-1]["inference"] == "not-run"
    assert not list((data_dir / ".incoming").glob("*"))
    listed = client.get("/api/v1/sessions").json()
    assert listed[0]["id"] == session["id"]
    assert listed[0]["processed_frames"] == 3

    deleted = client.delete(f"/api/v1/sessions/{session['id']}")
    assert deleted.status_code == 204
    assert client.get(session["result_url"]).status_code == 404


def test_invalid_video_is_reported_as_failed_session(
    session_client: tuple[TestClient, Path],
) -> None:
    client, _ = session_client
    response = client.post(
        "/api/v1/sessions/video?filename=broken.mp4",
        content=b"not a video",
        headers={"content-type": "video/mp4"},
    )

    assert response.status_code == 202
    session = _wait_for_session(client, response.json()["id"])
    assert session["status"] == "failed"
    assert "readable video" in session["error"]


def test_persisted_failed_session_keeps_its_diagnostic(
    session_client: tuple[TestClient, Path],
) -> None:
    client, data_dir = session_client
    engine = create_engine(f"sqlite:///{data_dir / 'sessions.sqlite'}")
    session_id = str(uuid4())
    source_id = str(uuid4())
    diagnostic = "Processing was interrupted when the API restarted. Start a new analysis."
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO sources (id, source_type, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (source_id, "video"),
        )
        connection.exec_driver_sql(
            "INSERT INTO sessions (id, source_id, status, created_at, error) "
            "VALUES (?, ?, 'failed', CURRENT_TIMESTAMP, ?)",
            (session_id, source_id, diagnostic),
        )

    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json()["error"] == diagnostic
    engine.dispose()


def test_video_upload_rejects_unsupported_extensions(
    session_client: tuple[TestClient, Path],
) -> None:
    client, _ = session_client
    response = client.post(
        "/api/v1/sessions/video?filename=notes.txt",
        content=b"not a video",
        headers={"content-type": "application/octet-stream"},
    )
    assert response.status_code == 415


def test_video_pipeline_records_detector_output_by_frame(tmp_path: Path) -> None:
    path = tmp_path / "detections.avi"
    _make_test_video(path)
    records: list[dict[str, object]] = []
    metadata, count, stopped = process_video(
        path,
        records.append,
        lambda _: None,
        session_id="synthetic-test",
        detect_frame=lambda _: [
            {"class_id": 3, "label": "car", "confidence": 0.91, "bbox_xyxy": [1.0, 2.0, 30.0, 40.0]}
        ],
    )
    assert count == 3 and not stopped
    assert metadata.width == 64
    assert all(record["inference"] == "complete" for record in records)
    assert all(record["detections"][0]["label"] == "car" for record in records)


def test_session_control_pauses_resumes_and_stops_cleanly() -> None:
    control = SessionControl()
    assert control.should_continue()

    control.pause()
    resumed: list[bool] = []
    worker = threading.Thread(target=lambda: resumed.append(control.should_continue()))
    worker.start()
    time.sleep(0.05)
    assert resumed == []

    control.resume()
    worker.join(timeout=1)
    assert resumed == [True]

    control.pause()
    control.stop()
    assert not control.should_continue()


def test_recovery_requeues_interrupted_video_once_from_retained_upload(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'recovery.sqlite'}")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE sources (id VARCHAR(36) PRIMARY KEY, source_type VARCHAR(32), "
            "source_metadata TEXT, created_at DATETIME NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY, source_id VARCHAR(36), "
            "status VARCHAR(32) NOT NULL, created_at DATETIME NOT NULL, ended_at DATETIME, "
            "camera_config JSON, error TEXT, analysis_fps FLOAT, "
            "restart_count INTEGER NOT NULL DEFAULT 0)"
        )
        connection.exec_driver_sql(
            "INSERT INTO sources (id, source_type, created_at) "
            "VALUES ('source-id', 'video', CURRENT_TIMESTAMP)"
        )
        connection.exec_driver_sql(
            "INSERT INTO sessions (id, source_id, status, created_at, analysis_fps) "
            "VALUES ('session-id', 'source-id', 'processing', CURRENT_TIMESTAMP, 3.5)"
        )
    upload = tmp_path / "uploads" / "session-id.mp4"
    upload.parent.mkdir()
    upload.write_bytes(b"retained video")
    results = tmp_path / "sessions" / "session-id" / "results.jsonl"
    results.parent.mkdir(parents=True)
    results.write_text("partial output", encoding="utf-8")
    registry = SessionRegistry()

    recovered = recover_interrupted_sessions(Settings(data_dir=tmp_path), engine, registry)

    assert len(recovered) == 1
    state, recovered_upload = recovered[0]
    assert recovered_upload == upload
    assert state.status == "queued"
    assert state.analysis_fps == 3.5
    assert registry.get("session-id") is state
    assert not results.exists()
    with engine.connect() as connection:
        row = connection.exec_driver_sql(
            "SELECT status, restart_count, error FROM sessions WHERE id='session-id'"
        ).one()
    assert row == ("queued", 1, None)

    # A second restart does not retry indefinitely.
    again = recover_interrupted_sessions(Settings(data_dir=tmp_path), engine, SessionRegistry())
    assert again == []
    with engine.connect() as connection:
        row = connection.exec_driver_sql(
            "SELECT status, restart_count, error FROM sessions WHERE id='session-id'"
        ).one()
    assert row[0] == "failed" and row[1] == 1
    assert "interrupted again" in row[2]
    engine.dispose()


def test_browser_camera_stream_echoes_frame_ids_and_exports_results(
    session_client: tuple[TestClient, Path],
) -> None:
    client, _ = session_client
    created = client.post("/api/v1/sessions/live")
    assert created.status_code == 201
    session_id = created.json()["id"]
    ok, encoded = cv2.imencode(".jpg", np.full((48, 64, 3), 90, dtype=np.uint8))
    assert ok

    with client.websocket_connect(f"/api/v1/sessions/ws/{session_id}") as websocket:
        assert websocket.receive_json()["type"] == "session_started"
        websocket.send_json(
            {
                "protocol": "rodai.v1",
                "type": "frame",
                "frame_id": 7,
                "capture_timestamp_ms": 1234.5,
                "dropped_since_last": 2,
            }
        )
        websocket.send_bytes(encoded.tobytes())
        result = websocket.receive_json()
        assert result["type"] == "frame_result"
        assert result["frame_id"] == 7
        assert result["capture_timestamp_ms"] == 1234.5
        assert result["processed_frames"] == 1
        assert result["dropped_frames"] == 2
        websocket.send_json({"protocol": "rodai.v1", "type": "stop", "dropped_since_last": 3})
        ended = websocket.receive_json()
        assert ended["type"] == "session_ended"
        assert ended["status"] == "stopped"

    session = client.get(f"/api/v1/sessions/{session_id}").json()
    assert session["status"] == "stopped"
    records = [json.loads(line) for line in client.get(session["result_url"]).text.splitlines()]
    assert records[0]["frame_id"] == 7
    assert records[0]["width"] == 64
    assert records[-1]["dropped_frames"] == 5
    assert client.delete(f"/api/v1/sessions/{session_id}").status_code == 204


def test_camera_settings_are_validated_negotiated_and_session_cap_is_enforced(
    session_client: tuple[TestClient, Path],
) -> None:
    client, _ = session_client
    first = client.post(
        "/api/v1/sessions/live",
        json={
            "max_width": 640,
            "max_height": 360,
            "jpeg_quality": 0.7,
        },
    )
    assert first.status_code == 201
    assert first.json()["camera_settings"] == {
        "max_width": 640,
        "max_height": 360,
        "jpeg_quality": 0.7,
    }
    conflict = client.post("/api/v1/sessions/live")
    assert conflict.status_code == 409
    invalid = client.post(
        "/api/v1/sessions/live",
        json={
            "max_width": 1920,
            "max_height": 1080,
            "jpeg_quality": 1.0,
        },
    )
    assert invalid.status_code == 422

    with client.websocket_connect(f"/api/v1/sessions/ws/{first.json()['id']}") as websocket:
        start = websocket.receive_json()
        assert start["capture_settings"] == first.json()["camera_settings"]
        websocket.send_json({"protocol": "rodai.v1", "type": "stop"})
        assert websocket.receive_json()["type"] == "session_ended"
