"""Video validation and lossless frame-echo processing for Phase 2."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2

from rodai.risk import evaluate_trajectory_cues
from rodai.tracking import RoadObjectTracker


class InvalidVideoError(ValueError):
    """The upload could not be opened and decoded as a video."""


@dataclass(frozen=True)
class VideoMetadata:
    width: int
    height: int
    fps: float | None
    reported_frame_count: int | None
    duration_ms: int | None


def _positive_finite(value: float) -> float | None:
    return value if math.isfinite(value) and value > 0 else None


def process_video(
    video_path: Path,
    write_record: Callable[[dict[str, Any]], None],
    progress: Callable[[int], None],
    *,
    session_id: str,
    max_video_seconds: int | None = None,
    analysis_fps: float | None = None,
    should_continue: Callable[[], bool] | None = None,
    detect_frame: Callable[[Any], list[dict[str, Any]]] | None = None,
) -> tuple[VideoMetadata, int, bool]:
    """Decode in order and emit records for analyzed frames at the configured sample rate."""
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise InvalidVideoError("The uploaded file is not a readable video.")

    try:
        raw_fps = _positive_finite(float(capture.get(cv2.CAP_PROP_FPS)))
        raw_count = float(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        reported_count = int(raw_count) if math.isfinite(raw_count) and raw_count > 0 else None
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration_ms = round(reported_count / raw_fps * 1000) if reported_count and raw_fps else None
        if max_video_seconds and duration_ms and duration_ms > max_video_seconds * 1000:
            raise InvalidVideoError(f"Video exceeds the {max_video_seconds} second duration limit.")

        frame_id = 0
        stopped = False
        tracker = RoadObjectTracker()
        last_timestamp_ms: int | None = None
        last_inference_timestamp_ms: int | None = None
        analyzed_frames = 0
        while True:
            if should_continue is not None and not should_continue():
                stopped = True
                break
            ok, frame = capture.read()
            if not ok:
                break
            if frame is None or getattr(frame, "ndim", 0) < 2:
                raise InvalidVideoError("The video decoder returned an invalid frame.")
            if width <= 0:
                width = int(frame.shape[1])
            if height <= 0:
                height = int(frame.shape[0])

            raw_timestamp = float(capture.get(cv2.CAP_PROP_POS_MSEC))
            fallback_timestamp = round(frame_id / raw_fps * 1000) if raw_fps else None
            timestamp_ms = (
                round(raw_timestamp)
                if math.isfinite(raw_timestamp) and raw_timestamp >= 0
                else None
            )
            if timestamp_ms is None or (
                last_timestamp_ms is not None and timestamp_ms <= last_timestamp_ms
            ):
                timestamp_ms = fallback_timestamp
            if timestamp_ms is not None:
                last_timestamp_ms = timestamp_ms
            if (
                max_video_seconds
                and timestamp_ms is not None
                and timestamp_ms > max_video_seconds * 1000
            ):
                raise InvalidVideoError(
                    f"Video exceeds the {max_video_seconds} second duration limit."
                )
            due_for_inference = (
                detect_frame is None
                or analysis_fps is None
                or timestamp_ms is None
                or last_inference_timestamp_ms is None
                or timestamp_ms - last_inference_timestamp_ms >= 1000 / analysis_fps
            )
            if not due_for_inference:
                frame_id += 1
                continue

            detections = detect_frame(frame) if detect_frame else []
            tracks = (
                tracker.update(detections, timestamp_ms=timestamp_ms, frame_id=frame_id)
                if detect_frame
                else []
            )
            risk_cues = evaluate_trajectory_cues(
                tracks, frame_id=frame_id, timestamp_ms=timestamp_ms
            )
            analyzed_frames += 1
            if detect_frame and timestamp_ms is not None:
                last_inference_timestamp_ms = timestamp_ms
            write_record(
                {
                    "schema_version": "rodai.session.v1",
                    "type": "frame",
                    "session_id": session_id,
                    "frame_id": frame_id,
                    "timestamp_ms": timestamp_ms,
                    "width": width,
                    "height": height,
                    "detections": detections,
                    "tracks": tracks,
                    "risk_cues": risk_cues,
                    "inference": "complete" if detect_frame else "not-run",
                }
            )
            frame_id += 1
            progress(analyzed_frames)

        if analyzed_frames == 0 and not stopped:
            raise InvalidVideoError("The uploaded video contains no decodable frames.")
        metadata = VideoMetadata(width, height, raw_fps, reported_count, duration_ms)
        return metadata, analyzed_frames, stopped
    finally:
        capture.release()


def write_jsonl_session(
    video_path: Path,
    result_path: Path,
    progress: Callable[[int], None],
    *,
    session_id: str,
    max_video_seconds: int | None = None,
    analysis_fps: float | None = None,
    should_continue: Callable[[], bool] | None = None,
    detect_frame: Callable[[Any], list[dict[str, Any]]] | None = None,
) -> tuple[VideoMetadata, int, bool]:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", encoding="utf-8", newline="\n") as output:

        def write_record(record: dict[str, Any]) -> None:
            output.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n")
            if record.get("type") == "frame" and record["frame_id"] % 25 == 0:
                output.flush()

        metadata, processed_frames, stopped = process_video(
            video_path,
            write_record,
            progress,
            session_id=session_id,
            max_video_seconds=max_video_seconds,
            analysis_fps=analysis_fps,
            should_continue=should_continue,
            detect_frame=detect_frame,
        )
        summary = {
            "schema_version": "rodai.session.v1",
            "type": "summary",
            "session_id": session_id,
            "processed_frames": processed_frames,
            "video": asdict(metadata),
            "analysis_fps": analysis_fps if detect_frame else None,
            "inference": "complete" if detect_frame and processed_frames > 0 else "not-run",
            "status": "stopped" if stopped else "completed",
        }
        write_record(summary)
    return metadata, processed_frames, stopped
