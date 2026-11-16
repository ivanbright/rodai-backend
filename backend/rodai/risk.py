"""Evidence-only image-plane trajectory cues for human review.

These cues are deterministic geometry from prototype tracks. They are not
collision predictions, calibrated risk probabilities, or safety instructions.
"""

from __future__ import annotations

import math
from typing import Any

MIN_CONFIDENCE = 0.45
MIN_TIME_SECONDS = 0.15
MAX_HORIZON_SECONDS = 3.0
MIN_RELATIVE_SPEED_PX_S = 1.0
BOUNDING_BOX_MARGIN_PX = 8.0


def evaluate_trajectory_cues(
    tracks: list[dict[str, Any]], *, frame_id: int, timestamp_ms: int | float | None
) -> list[dict[str, Any]]:
    """Return review cues when projected track centers approach within box size.

    The projection uses uncalibrated image pixels and assumes constant velocity.
    Sparse samples, detection noise, perspective and prototype IDs can all make
    the result wrong. Callers should present this as a review cue only.
    """
    valid = [track for track in tracks if _valid_track(track)]
    cues: list[dict[str, Any]] = []
    for first_index, first in enumerate(valid):
        for second in valid[first_index + 1 :]:
            first_id = int(first["track_id"])
            second_id = int(second["track_id"])
            if first_id == second_id:
                continue

            first_center = first["center_xy"]
            second_center = second["center_xy"]
            first_velocity = first["velocity_px_s"]
            second_velocity = second["velocity_px_s"]
            relative_x = second_center[0] - first_center[0]
            relative_y = second_center[1] - first_center[1]
            relative_velocity_x = second_velocity[0] - first_velocity[0]
            relative_velocity_y = second_velocity[1] - first_velocity[1]
            relative_speed_squared = relative_velocity_x**2 + relative_velocity_y**2
            if relative_speed_squared < MIN_RELATIVE_SPEED_PX_S**2:
                continue

            time = -(
                relative_x * relative_velocity_x + relative_y * relative_velocity_y
            ) / relative_speed_squared
            if not MIN_TIME_SECONDS <= time <= MAX_HORIZON_SECONDS:
                continue

            closest_x = relative_x + relative_velocity_x * time
            closest_y = relative_y + relative_velocity_y * time
            first_box = first["bbox_xyxy"]
            second_box = second["bbox_xyxy"]
            already_overlapping = (
                first_box[0] < second_box[2]
                and second_box[0] < first_box[2]
                and first_box[1] < second_box[3]
                and second_box[1] < first_box[3]
            )
            if already_overlapping:
                continue
            first_width = first_box[2] - first_box[0]
            first_height = first_box[3] - first_box[1]
            second_width = second_box[2] - second_box[0]
            second_height = second_box[3] - second_box[1]
            allowed_x = (first_width + second_width) / 2 + BOUNDING_BOX_MARGIN_PX
            allowed_y = (first_height + second_height) / 2 + BOUNDING_BOX_MARGIN_PX
            margin_x = allowed_x - abs(closest_x)
            margin_y = allowed_y - abs(closest_y)
            if margin_x < 0 or margin_y < 0:
                continue

            track_ids = sorted((first_id, second_id))
            by_id = {int(first["track_id"]): first, int(second["track_id"]): second}
            ordered = [by_id[track_id] for track_id in track_ids]
            cues.append(
                {
                    "cue_id": f"{frame_id}:{track_ids[0]}:{track_ids[1]}",
                    "cue_type": "trajectory_convergence",
                    "status": "review",
                    "frame_id": frame_id,
                    "timestamp_ms": timestamp_ms,
                    "track_ids": track_ids,
                    "labels": [str(track.get("label", "road user")) for track in ordered],
                    "time_to_closest_approach_seconds": round(time, 2),
                    "closest_center_separation_px": round(
                        math.hypot(closest_x, closest_y), 1
                    ),
                    "projected_box_margin_px": [
                        round(margin_x, 1),
                        round(margin_y, 1),
                    ],
                    "method": "constant_velocity_image_plane",
                    "calibrated": False,
                }
            )

    return sorted(
        cues, key=lambda cue: (cue["time_to_closest_approach_seconds"], cue["track_ids"])
    )


def _valid_track(track: dict[str, Any]) -> bool:
    try:
        track_id = track["track_id"]
        confidence = float(track["confidence"])
        box = [float(value) for value in track["bbox_xyxy"]]
        center = [float(value) for value in track["center_xy"]]
        velocity = [float(value) for value in track["velocity_px_s"]]
        trail = track["trail_xy"]
    except (KeyError, TypeError, ValueError):
        return False
    return (
        isinstance(track_id, int)
        and math.isfinite(confidence)
        and confidence >= MIN_CONFIDENCE
        and len(box) == 4
        and all(math.isfinite(value) for value in box)
        and box[2] > box[0]
        and box[3] > box[1]
        and len(center) == 2
        and all(math.isfinite(value) for value in center)
        and len(velocity) == 2
        and all(math.isfinite(value) for value in velocity)
        and isinstance(trail, list)
        and len(trail) >= 3
    )
