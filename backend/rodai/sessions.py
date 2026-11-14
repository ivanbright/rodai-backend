"""HTTP API for uploaded-video sessions and frame-aligned exports."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import shutil
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import cv2
import numpy as np
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Query,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import Engine, text

from rodai.config import Settings
from rodai.video_pipeline import InvalidVideoError, write_jsonl_session

logger = logging.getLogger("rodai.sessions")

VIDEO_SUFFIXES = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}


@dataclass
class SessionState:
    id: str
    filename: str
    status: str
    created_at: str
    uploaded_bytes: int
    source_type: str = "video"
    processed_frames: int = 0
    metadata: dict[str, Any] | None = None
    error: str | None = None

    def response(self) -> dict[str, Any]:
        return asdict(self) | {"result_url": f"/api/v1/sessions/{self.id}/results"}


@dataclass
class SessionControl:
    resume_event: threading.Event = field(default_factory=threading.Event)
    stop_event: threading.Event = field(default_factory=threading.Event)

    def __post_init__(self) -> None:
        self.resume_event.set()

    def pause(self) -> None:
        self.resume_event.clear()

    def resume(self) -> None:
        self.resume_event.set()

    def stop(self) -> None:
        self.stop_event.set()
        self.resume_event.set()

    def should_continue(self) -> bool:
        while not self.stop_event.is_set():
            if self.resume_event.wait(timeout=0.1):
                return True
        return False


class SessionRegistry:
    def __init__(self) -> None:
        self._items: dict[str, SessionState] = {}
        self._controls: dict[str, SessionControl] = {}
        self._lock = threading.RLock()

    def add(self, state: SessionState, maximum_active: int) -> None:
        with self._lock:
            active = sum(
                item.status in {"uploading", "queued", "processing", "paused", "stopping"}
                for item in self._items.values()
            )
            if active >= maximum_active:
                raise RuntimeError("The configured number of video sessions is already active.")
            self._items[state.id] = state
            self._controls[state.id] = SessionControl()

    def get(self, session_id: str) -> SessionState | None:
        with self._lock:
            return self._items.get(session_id)

    def update(self, session_id: str, **values: Any) -> None:
        with self._lock:
            item = self._items.get(session_id)
            if item:
                for key, value in values.items():
                    setattr(item, key, value)

    def control(self, session_id: str) -> SessionControl | None:
        with self._lock:
            return self._controls.get(session_id)

    def remove(self, session_id: str) -> None:
        with self._lock:
            self._items.pop(session_id, None)
            self._controls.pop(session_id, None)


def make_sessions_router(settings: Settings, engine: Engine) -> APIRouter:
    router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])
    registry = SessionRegistry()
    incoming_dir = settings.data_dir / ".incoming"
    sessions_dir = settings.data_dir / "sessions"

    @router.get("")
    def list_sessions(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, Any]]:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    "SELECT s.id, s.status, s.created_at, src.source_type "
                    "FROM sessions AS s LEFT JOIN sources AS src ON src.id = s.source_id "
                    "ORDER BY s.created_at DESC LIMIT :limit"
                ),
                {"limit": limit},
            ).mappings()
            items = []
            for row in rows:
                session_id = str(row["id"])
                current = registry.get(session_id)
                if current:
                    items.append(current.response())
                    continue
                items.append(
                    _persisted_session(
                        settings,
                        session_id,
                        row["status"],
                        row["created_at"],
                        row["source_type"] or "video",
                    )
                )
        return items

    @router.post("/video", status_code=status.HTTP_202_ACCEPTED)
    async def upload_video(
        request: Request,
        background_tasks: BackgroundTasks,
        filename: str,
    ) -> dict[str, Any]:
        suffix = Path(filename).suffix.lower()
        if suffix not in VIDEO_SUFFIXES:
            raise HTTPException(
                415, "Choose a supported video file (MP4, MOV, MKV, WebM, or AVI)."
            )
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
        if (
            content_type
            and not content_type.startswith("video/")
            and content_type != "application/octet-stream"
        ):
            raise HTTPException(415, "The request must contain video bytes.")

        state_id = str(uuid4())
        try:
            registry.add(
                SessionState(
                    id=state_id,
                    filename=Path(filename).name,
                    status="uploading",
                    created_at=datetime.now(UTC).isoformat(),
                    uploaded_bytes=0,
                ),
                settings.max_concurrent_sessions,
            )
        except RuntimeError as exc:
            raise HTTPException(409, str(exc)) from exc

        upload_path = incoming_dir / f"{state_id}{suffix}"
        byte_limit = settings.max_upload_mb * 1024 * 1024
        received = 0
        try:
            incoming_dir.mkdir(parents=True, exist_ok=True)
            with upload_path.open("wb") as output:
                async for chunk in request.stream():
                    received += len(chunk)
                    if received > byte_limit:
                        raise HTTPException(
                            413,
                            f"Video exceeds the {settings.max_upload_mb} MB upload limit.",
                        )
                    output.write(chunk)
            if received == 0:
                raise HTTPException(400, "The uploaded video is empty.")
            registry.update(state_id, uploaded_bytes=received, status="queued")
            await asyncio.to_thread(_create_database_session, engine, state_id)
        except HTTPException:
            upload_path.unlink(missing_ok=True)
            registry.remove(state_id)
            raise
        except Exception as exc:
            upload_path.unlink(missing_ok=True)
            registry.remove(state_id)
            logger.exception("Failed to create video session")
            raise HTTPException(
                503,
                "Could not create a video session. Check the database and data volume.",
            ) from exc

        background_tasks.add_task(
            _process_video,
            engine,
            settings,
            registry,
            state_id,
            upload_path,
            sessions_dir / state_id / "results.jsonl",
        )
        state = registry.get(state_id)
        assert state is not None
        return state.response()

    @router.post("/live", status_code=status.HTTP_201_CREATED)
    def create_live_session() -> dict[str, Any]:
        session_id = str(uuid4())
        state = SessionState(
            id=session_id,
            filename="Browser camera",
            status="queued",
            created_at=datetime.now(UTC).isoformat(),
            uploaded_bytes=0,
            source_type="browser_camera",
        )
        try:
            registry.add(state, settings.max_concurrent_sessions)
            (sessions_dir / session_id).mkdir(parents=True, exist_ok=True)
            _create_database_session(engine, session_id, source_type="browser_camera")
        except RuntimeError as exc:
            registry.remove(session_id)
            raise HTTPException(409, str(exc)) from exc
        except Exception as exc:
            registry.remove(session_id)
            shutil.rmtree(sessions_dir / session_id, ignore_errors=True)
            logger.exception("Failed to create browser camera session")
            raise HTTPException(503, "Could not create a camera session.") from exc
        return state.response()

    @router.websocket("/ws/{session_id}")
    async def browser_camera(websocket: WebSocket, session_id: str) -> None:
        try:
            parsed_id = str(UUID(session_id))
        except ValueError:
            await websocket.close(code=1008, reason="Unknown session")
            return
        state = registry.get(parsed_id)
        control = registry.control(parsed_id)
        if not state or not control or state.source_type != "browser_camera":
            await websocket.close(code=1008, reason="Unknown camera session")
            return

        await websocket.accept()
        registry.update(parsed_id, status="processing")
        _update_session_status(engine, parsed_id, "processing")
        result_path = sessions_dir / parsed_id / "results.jsonl"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        output = result_path.open("w", encoding="utf-8", newline="\n")
        start_time = time.monotonic()
        processed_frames = 0
        dropped_frames = 0
        last_frame_id = -1
        width = 0
        height = 0
        final_status = "stopped"
        failure_message: str | None = None
        try:
            await websocket.send_json(
                {"protocol": "rodai.v1", "type": "session_started", "session_id": parsed_id}
            )
            while True:
                remaining_seconds = settings.max_video_seconds - (time.monotonic() - start_time)
                if remaining_seconds <= 0:
                    break
                try:
                    message = await asyncio.wait_for(
                        websocket.receive_json(), timeout=remaining_seconds
                    )
                except TimeoutError:
                    break
                if not isinstance(message, dict) or message.get("protocol") != "rodai.v1":
                    await websocket.send_json(
                        {"protocol": "rodai.v1", "type": "error", "code": "invalid_message"}
                    )
                    continue
                message_type = message.get("type")
                if message_type == "stop":
                    break
                if message_type != "frame":
                    await websocket.send_json(
                        {"protocol": "rodai.v1", "type": "error", "code": "unsupported_message"}
                    )
                    continue

                jpeg_bytes = await websocket.receive_bytes()
                frame_id = message.get("frame_id")
                capture_time = message.get("capture_timestamp_ms")
                dropped = message.get("dropped_since_last", 0)
                if (
                    not isinstance(frame_id, int)
                    or isinstance(frame_id, bool)
                    or frame_id <= last_frame_id
                    or not isinstance(capture_time, int | float)
                    or isinstance(capture_time, bool)
                    or not math.isfinite(capture_time)
                    or not isinstance(dropped, int)
                    or isinstance(dropped, bool)
                    or dropped < 0
                    or len(jpeg_bytes) > 10 * 1024 * 1024
                ):
                    await websocket.send_json(
                        {
                            "protocol": "rodai.v1",
                            "type": "error",
                            "code": "invalid_frame_metadata",
                            "frame_id": frame_id,
                        }
                    )
                    continue

                if not await asyncio.to_thread(control.should_continue):
                    break
                frame = cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    await websocket.send_json(
                        {
                            "protocol": "rodai.v1",
                            "type": "error",
                            "code": "invalid_frame_data",
                            "frame_id": frame_id,
                        }
                    )
                    continue
                height, width = int(frame.shape[0]), int(frame.shape[1])
                last_frame_id = frame_id
                dropped_frames += dropped
                processed_frames += 1
                server_time = datetime.now(UTC).isoformat()
                frame_record = {
                    "schema_version": "rodai.session.v1",
                    "type": "frame",
                    "protocol": "rodai.v1",
                    "session_id": parsed_id,
                    "frame_id": frame_id,
                    "capture_timestamp_ms": capture_time,
                    "server_received_at": server_time,
                    "width": width,
                    "height": height,
                    "dropped_since_last": dropped,
                    "detections": [],
                    "tracks": [],
                    "inference": "not-run",
                }
                output.write(json.dumps(frame_record, separators=(",", ":")) + "\n")
                output.flush()
                elapsed_ms = round((time.monotonic() - start_time) * 1000)
                metadata = {
                    "width": width,
                    "height": height,
                    "fps": None,
                    "reported_frame_count": None,
                    "duration_ms": elapsed_ms,
                }
                registry.update(
                    parsed_id,
                    processed_frames=processed_frames,
                    metadata=metadata,
                )
                await websocket.send_json(
                    {
                        "protocol": "rodai.v1",
                        "type": "frame_result",
                        "session_id": parsed_id,
                        "frame_id": frame_id,
                        "capture_timestamp_ms": capture_time,
                        "server_received_at": server_time,
                        "processed_frames": processed_frames,
                        "dropped_frames": dropped_frames,
                        "width": width,
                        "height": height,
                        "duration_ms": elapsed_ms,
                        "inference": "not-run",
                    }
                )
        except WebSocketDisconnect:
            final_status = "stopped"
        except Exception:
            logger.exception("Browser camera session failed session_id=%s", parsed_id)
            final_status = "failed"
            failure_message = "Camera stream failed. Start a new camera session."
        finally:
            elapsed_ms = round((time.monotonic() - start_time) * 1000)
            output.write(
                json.dumps(
                    {
                        "schema_version": "rodai.session.v1",
                        "type": "summary",
                        "session_id": parsed_id,
                        "source_type": "browser_camera",
                        "processed_frames": processed_frames,
                        "dropped_frames": dropped_frames,
                        "width": width,
                        "height": height,
                        "duration_ms": elapsed_ms,
                        "inference": "not-run",
                        "status": final_status,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
            output.close()
            if final_status == "failed":
                result_path.unlink(missing_ok=True)
            final_metadata = {
                "width": width,
                "height": height,
                "fps": None,
                "reported_frame_count": processed_frames,
                "duration_ms": elapsed_ms,
            }
            registry.update(
                parsed_id,
                status=final_status,
                processed_frames=processed_frames,
                metadata=final_metadata if width and height else None,
                error=failure_message,
            )
            try:
                _update_session_status(engine, parsed_id, final_status, ended=True)
            except Exception:
                logger.exception(
                    "Could not persist browser session status session_id=%s", parsed_id
                )
            try:
                await websocket.send_json(
                    {
                        "protocol": "rodai.v1",
                        "type": "session_ended",
                        "session_id": parsed_id,
                        "status": final_status,
                        "processed_frames": processed_frames,
                        "dropped_frames": dropped_frames,
                    }
                )
                await websocket.close()
            except Exception:
                pass

    @router.get("/{session_id}")
    def get_session(session_id: str) -> dict[str, Any]:
        parsed_id = _parse_id(session_id)
        state = registry.get(parsed_id)
        if state:
            return state.response()
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT s.id, s.status, s.created_at, src.source_type "
                    "FROM sessions AS s LEFT JOIN sources AS src ON src.id = s.source_id "
                    "WHERE s.id = :id"
                ),
                {"id": parsed_id},
            ).mappings().first()
        if not row:
            raise HTTPException(404, "Session not found.")
        return _persisted_session(
            settings,
            parsed_id,
            row["status"],
            row["created_at"],
            row["source_type"] or "video",
        )

    @router.post("/{session_id}/pause")
    def pause_session(session_id: str) -> dict[str, Any]:
        parsed_id = _parse_id(session_id)
        state = registry.get(parsed_id)
        control = registry.control(parsed_id)
        if not state or not control:
            raise HTTPException(404, "Active session not found.")
        if state.status != "processing":
            raise HTTPException(409, "Only a processing session can be paused.")
        control.pause()
        registry.update(parsed_id, status="paused")
        _update_session_status(engine, parsed_id, "paused")
        return state.response()

    @router.post("/{session_id}/resume")
    def resume_session(session_id: str) -> dict[str, Any]:
        parsed_id = _parse_id(session_id)
        state = registry.get(parsed_id)
        control = registry.control(parsed_id)
        if not state or not control:
            raise HTTPException(404, "Active session not found.")
        if state.status != "paused":
            raise HTTPException(409, "Only a paused session can be resumed.")
        control.resume()
        registry.update(parsed_id, status="processing")
        _update_session_status(engine, parsed_id, "processing")
        return state.response()

    @router.post("/{session_id}/stop")
    def stop_session(session_id: str) -> dict[str, Any]:
        parsed_id = _parse_id(session_id)
        state = registry.get(parsed_id)
        control = registry.control(parsed_id)
        if not state or not control:
            raise HTTPException(404, "Active session not found.")
        if state.status not in {"uploading", "queued", "processing", "paused"}:
            raise HTTPException(409, "Session is not active.")
        control.stop()
        registry.update(parsed_id, status="stopping")
        _update_session_status(engine, parsed_id, "stopping")
        return state.response()

    @router.get("/{session_id}/results")
    def get_results(session_id: str) -> FileResponse:
        parsed_id = _parse_id(session_id)
        result_path = sessions_dir / parsed_id / "results.jsonl"
        state = registry.get(parsed_id)
        if state and state.status not in {"completed", "stopped"}:
            raise HTTPException(409, "Session results are not ready yet.")
        if not result_path.is_file():
            if state is None:
                raise HTTPException(404, "Session result is not available.")
            raise HTTPException(404, "Session result is not available.")
        return FileResponse(
            result_path,
            media_type="application/x-ndjson",
            filename=f"rodai-session-{parsed_id}.jsonl",
        )

    @router.delete(
        "/{session_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
    )
    def delete_session(session_id: str) -> Response:
        parsed_id = _parse_id(session_id)
        state = registry.get(parsed_id)
        if state and state.status in {
            "uploading", "queued", "processing", "paused", "stopping"
        }:
            raise HTTPException(409, "Stop or wait for the active session before deleting it.")
        with engine.begin() as connection:
            row = connection.execute(
                text("SELECT source_id FROM sessions WHERE id = :id"), {"id": parsed_id}
            ).first()
            if not row:
                raise HTTPException(404, "Session not found.")
            source_id = row[0]
            connection.execute(text("DELETE FROM events WHERE session_id = :id"), {"id": parsed_id})
            connection.execute(
                text("DELETE FROM session_results WHERE session_id = :id"),
                {"id": parsed_id},
            )
            connection.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": parsed_id})
            if source_id:
                connection.execute(text("DELETE FROM sources WHERE id = :id"), {"id": source_id})
        shutil.rmtree(sessions_dir / parsed_id, ignore_errors=True)
        registry.remove(parsed_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


def _parse_id(value: str) -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise HTTPException(404, "Session not found.") from exc


def _persisted_session(
    settings: Settings,
    session_id: str,
    session_status: str,
    created_at: datetime | str,
    source_type: str = "video",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": session_id,
        "filename": "Browser camera" if source_type == "browser_camera" else "Uploaded video",
        "source_type": source_type,
        "status": session_status,
        "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
        "uploaded_bytes": 0,
        "processed_frames": 0,
        "metadata": None,
        "error": None,
        "result_url": f"/api/v1/sessions/{session_id}/results",
    }
    result_path = settings.data_dir / "sessions" / session_id / "results.jsonl"
    if session_status in {"completed", "stopped"} and result_path.is_file():
        try:
            tail = result_path.read_bytes()[-4096:]
            summary_line = tail.splitlines()[-1]
            summary = json.loads(summary_line)
            result["processed_frames"] = summary.get("processed_frames", 0)
            result["metadata"] = summary.get("video") or {
                "width": summary.get("width", 0),
                "height": summary.get("height", 0),
                "fps": None,
                "reported_frame_count": summary.get("processed_frames"),
                "duration_ms": summary.get("duration_ms"),
            }
        except (OSError, IndexError, ValueError, json.JSONDecodeError):
            logger.warning("Could not read session summary session_id=%s", session_id)
    return result


def _create_database_session(
    engine: Engine, session_id: str, *, source_type: str = "video"
) -> None:
    now = datetime.now(UTC)
    source_id = str(uuid4())
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO sources (id, source_type, created_at) "
                "VALUES (:id, :source_type, :created_at)"
            ),
            {"id": source_id, "source_type": source_type, "created_at": now},
        )
        connection.execute(
            text(
                "INSERT INTO sessions (id, source_id, status, created_at) "
                "VALUES (:id, :source_id, 'queued', :created_at)"
            ),
            {"id": session_id, "source_id": source_id, "created_at": now},
        )
        connection.execute(
            text(
                "INSERT INTO session_results "
                "(id, session_id, result_path, schema_version, created_at) "
                "VALUES (:id, :session_id, :result_path, 'rodai.session.v1', :created_at)"
            ),
            {
                "id": str(uuid4()),
                "session_id": session_id,
                "result_path": f"sessions/{session_id}/results.jsonl",
                "created_at": now,
            },
        )


def _update_session_status(
    engine: Engine, session_id: str, session_status: str, *, ended: bool = False
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE sessions SET status = :status, ended_at = :ended_at WHERE id = :id"),
            {
                "status": session_status,
                "ended_at": datetime.now(UTC) if ended else None,
                "id": session_id,
            },
        )


def recover_interrupted_sessions(settings: Settings, engine: Engine) -> None:
    """Mark sessions interrupted by an API restart and remove their temporary uploads."""
    try:
        with engine.begin() as connection:
            rows = connection.execute(
                text(
                    "SELECT id FROM sessions "
                    "WHERE status IN ('queued', 'processing', 'paused', 'stopping')"
                )
            ).scalars().all()
            if rows:
                connection.execute(
                    text(
                        "UPDATE sessions SET status = 'failed', ended_at = :ended_at "
                        "WHERE status IN ('queued', 'processing', 'paused', 'stopping')"
                    ),
                    {"ended_at": datetime.now(UTC)},
                )
        for session_id in rows:
            (settings.data_dir / "sessions" / str(session_id) / "results.jsonl").unlink(
                missing_ok=True
            )
        incoming_dir = settings.data_dir / ".incoming"
        if incoming_dir.is_dir():
            for upload_path in incoming_dir.iterdir():
                if upload_path.is_file():
                    upload_path.unlink(missing_ok=True)
        if rows:
            logger.warning("Marked %s interrupted video session(s) as failed", len(rows))
    except Exception:
        logger.exception("Could not recover interrupted video sessions")


def _process_video(
    engine: Engine,
    settings: Settings,
    registry: SessionRegistry,
    session_id: str,
    upload_path: Path,
    result_path: Path,
) -> None:
    try:
        registry.update(session_id, status="processing")
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE sessions SET status = 'processing' WHERE id = :id"),
                {"id": session_id},
            )
        control = registry.control(session_id)
        metadata, processed_frames, stopped = write_jsonl_session(
            upload_path,
            result_path,
            lambda value: registry.update(session_id, processed_frames=value),
            session_id=session_id,
            max_video_seconds=settings.max_video_seconds,
            should_continue=control.should_continue if control else None,
        )
        final_status = "stopped" if stopped else "completed"
        registry.update(
            session_id,
            status=final_status,
            processed_frames=processed_frames,
            metadata=asdict(metadata),
        )
        _update_session_status(engine, session_id, final_status, ended=True)
    except InvalidVideoError as exc:
        registry.update(session_id, status="failed", error=str(exc))
        result_path.unlink(missing_ok=True)
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE sessions SET status = 'failed', ended_at = :ended_at WHERE id = :id"),
                {"id": session_id, "ended_at": datetime.now(UTC)},
            )
    except Exception:
        logger.exception("Video session failed session_id=%s", session_id)
        registry.update(
            session_id,
            status="failed",
            error="Video processing failed. Check the video file and try again.",
        )
        result_path.unlink(missing_ok=True)
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE sessions SET status = 'failed', ended_at = :ended_at WHERE id = :id"),
                {"id": session_id, "ended_at": datetime.now(UTC)},
            )
    finally:
        upload_path.unlink(missing_ok=True)
