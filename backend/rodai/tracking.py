"""Lightweight online tracking for detector outputs from one fixed camera."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


def _center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def _iou(left: list[float], right: list[float]) -> float:
    x1, y1 = max(left[0], right[0]), max(left[1], right[1])
    x2, y2 = min(left[2], right[2]), min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union > 0 else 0.0


@dataclass
class _Track:
    track_id: int
    label: str
    bbox: list[float]
    center: tuple[float, float]
    timestamp_ms: float | None
    frame_id: int
    velocity_px_s: tuple[float, float] = (0.0, 0.0)
    confidence: float = 0.0
    trail: list[list[float]] = field(default_factory=list)


class RoadObjectTracker:
    """Associate same-class detections using predicted IoU and image-space motion.

    This is a practical prototype tracker, not a re-identification model. Speeds are
    image-plane pixels per second and must never be presented as physical road speed.
    """

    def __init__(self, *, max_gap_ms: int = 1200, trail_length: int = 16) -> None:
        self.max_gap_ms = max_gap_ms
        self.trail_length = trail_length
        self._next_id = 1
        self._tracks: dict[int, _Track] = {}

    def update(
        self,
        detections: list[dict[str, Any]],
        *,
        timestamp_ms: float | None,
        frame_id: int,
    ) -> list[dict[str, Any]]:
        if timestamp_ms is not None and not math.isfinite(timestamp_ms):
            timestamp_ms = None
        if timestamp_ms is not None:
            timestamp_ms = float(timestamp_ms)
        self._tracks = {
            track_id: track
            for track_id, track in self._tracks.items()
            if (
                track.timestamp_ms is not None
                and timestamp_ms is not None
                and 0 <= timestamp_ms - track.timestamp_ms <= self.max_gap_ms
            )
            or (
                (track.timestamp_ms is None or timestamp_ms is None)
                and 0 <= frame_id - track.frame_id <= 36
            )
        }

        boxes = [list(map(float, item["bbox_xyxy"])) for item in detections]
        centers = [_center(box) for box in boxes]
        candidates: list[tuple[float, int, int]] = []
        for track_id, track in self._tracks.items():
            elapsed_s = (
                max(0.0, timestamp_ms - track.timestamp_ms) / 1000.0
                if timestamp_ms is not None and track.timestamp_ms is not None
                else 0.0
            )
            predicted_center = (
                track.center[0] + track.velocity_px_s[0] * elapsed_s,
                track.center[1] + track.velocity_px_s[1] * elapsed_s,
            )
            predicted_box = [
                track.bbox[0] + predicted_center[0] - track.center[0],
                track.bbox[1] + predicted_center[1] - track.center[1],
                track.bbox[2] + predicted_center[0] - track.center[0],
                track.bbox[3] + predicted_center[1] - track.center[1],
            ]
            for index, detection in enumerate(detections):
                if str(detection.get("label", "")) != track.label:
                    continue
                distance = math.dist(predicted_center, centers[index])
                width = max(track.bbox[2] - track.bbox[0], boxes[index][2] - boxes[index][0])
                height = max(track.bbox[3] - track.bbox[1], boxes[index][3] - boxes[index][1])
                gate = max(32.0, math.hypot(width, height) * 0.85)
                overlap = _iou(predicted_box, boxes[index])
                if overlap >= 0.03 or distance <= gate:
                    score = 0.55 * overlap + 0.45 * max(0.0, 1 - distance / gate)
                    candidates.append((score, track_id, index))

        candidates.sort(reverse=True)
        matched_tracks: set[int] = set()
        matched_detections: set[int] = set()
        associations: dict[int, int] = {}
        for _, track_id, index in candidates:
            if track_id in matched_tracks or index in matched_detections:
                continue
            matched_tracks.add(track_id)
            matched_detections.add(index)
            associations[index] = track_id

        output: list[dict[str, Any]] = []
        for index, detection in enumerate(detections):
            center = centers[index]
            box = boxes[index]
            track_id = associations.get(index)
            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
                track = _Track(
                    track_id=track_id,
                    label=str(detection.get("label", "object")),
                    bbox=box,
                    center=center,
                    timestamp_ms=timestamp_ms,
                    frame_id=frame_id,
                    confidence=float(detection.get("confidence", 0.0)),
                    trail=[[round(center[0], 1), round(center[1], 1)]],
                )
                self._tracks[track_id] = track
            else:
                track = self._tracks[track_id]
                elapsed_s = (
                    (timestamp_ms - track.timestamp_ms) / 1000.0
                    if timestamp_ms is not None and track.timestamp_ms is not None
                    else 0.0
                )
                if elapsed_s > 0:
                    measured = (
                        (center[0] - track.center[0]) / elapsed_s,
                        (center[1] - track.center[1]) / elapsed_s,
                    )
                    track.velocity_px_s = (
                        0.45 * track.velocity_px_s[0] + 0.55 * measured[0],
                        0.45 * track.velocity_px_s[1] + 0.55 * measured[1],
                    )
                track.bbox = box
                track.center = center
                track.timestamp_ms = timestamp_ms
                track.frame_id = frame_id
                track.confidence = float(detection.get("confidence", 0.0))
                track.trail.append([round(center[0], 1), round(center[1], 1)])
                track.trail = track.trail[-self.trail_length :]

            speed = math.hypot(*track.velocity_px_s) if timestamp_ms is not None else None
            output.append(
                {
                    "track_id": track.track_id,
                    "label": track.label,
                    "confidence": round(track.confidence, 4),
                    "bbox_xyxy": [round(value, 2) for value in track.bbox],
                    "center_xy": [round(track.center[0], 1), round(track.center[1], 1)],
                    "velocity_px_s": [
                        round(track.velocity_px_s[0], 1),
                        round(track.velocity_px_s[1], 1),
                    ],
                    "speed_px_s": round(speed, 1) if speed is not None else None,
                    "trail_xy": track.trail.copy(),
                }
            )
        return output
