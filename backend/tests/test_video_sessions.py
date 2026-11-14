import json
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from rodai.config import Settings
from rodai.sessions import SessionControl, make_sessions_router


@pytest.fixture
def session_client(tmp_path: Path) -> tuple[TestClient, Path]:
    engine = create_engine(f"sqlite:///{tmp_path / 'sessions.sqlite'}")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE sources (id VARCHAR(36) PRIMARY KEY, source_type VARCHAR(32), "
            "created_at DATETIME NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY, source_id VARCHAR(36), "
            "status VARCHAR(32) NOT NULL, created_at DATETIME NOT NULL, ended_at DATETIME)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE session_results (id VARCHAR(36) PRIMARY KEY, session_id VARCHAR(36), "
            "result_path VARCHAR(1024), schema_version VARCHAR(32), created_at DATETIME)"
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
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"MJPG"), 5.0, (64, 48)
    )
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
        websocket.send_json({"protocol": "rodai.v1", "type": "stop"})
        ended = websocket.receive_json()
        assert ended["type"] == "session_ended"
        assert ended["status"] == "stopped"

    session = client.get(f"/api/v1/sessions/{session_id}").json()
    assert session["status"] == "stopped"
    records = [
        json.loads(line)
        for line in client.get(session["result_url"]).text.splitlines()
    ]
    assert records[0]["frame_id"] == 7
    assert records[0]["width"] == 64
    assert records[-1]["dropped_frames"] == 2
    assert client.delete(f"/api/v1/sessions/{session_id}").status_code == 204
