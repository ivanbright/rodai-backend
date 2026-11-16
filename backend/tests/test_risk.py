from rodai.risk import evaluate_trajectory_cues


def road_track(
    track_id: int,
    label: str,
    center: tuple[float, float],
    velocity: tuple[float, float],
    *,
    confidence: float = 0.9,
) -> dict:
    x, y = center
    return {
        "track_id": track_id,
        "label": label,
        "confidence": confidence,
        "bbox_xyxy": [x - 5, y - 5, x + 5, y + 5],
        "center_xy": [x, y],
        "velocity_px_s": list(velocity),
        "trail_xy": [[x - 2, y], [x - 1, y], [x, y]],
    }


def test_projected_overlap_emits_review_only_evidence():
    cues = evaluate_trajectory_cues(
        [
            road_track(8, "car", (0, 0), (10, 0)),
            road_track(3, "motorcycle", (50, 0), (-10, 0)),
        ],
        frame_id=42,
        timestamp_ms=2_500,
    )

    assert len(cues) == 1
    cue = cues[0]
    assert cue["cue_id"] == "42:3:8"
    assert cue["cue_type"] == "trajectory_convergence"
    assert cue["status"] == "review"
    assert cue["track_ids"] == [3, 8]
    assert cue["labels"] == ["motorcycle", "car"]
    assert cue["time_to_closest_approach_seconds"] == 2.5
    assert cue["method"] == "constant_velocity_image_plane"
    assert cue["calibrated"] is False
    assert "probability" not in cue


def test_diverging_or_low_confidence_tracks_do_not_emit_cue():
    diverging = [
        road_track(1, "car", (0, 0), (-10, 0)),
        road_track(2, "car", (50, 0), (10, 0)),
    ]
    low_confidence = [
        road_track(1, "car", (0, 0), (10, 0)),
        road_track(2, "car", (50, 0), (-10, 0), confidence=0.2),
    ]

    assert evaluate_trajectory_cues(diverging, frame_id=0, timestamp_ms=0) == []
    assert evaluate_trajectory_cues(low_confidence, frame_id=0, timestamp_ms=0) == []


def test_unstable_or_already_overlapping_tracks_do_not_emit_forward_cue():
    short_track = road_track(1, "car", (0, 0), (10, 0))
    short_track["trail_xy"] = [[-1, 0], [0, 0]]
    already_overlapping = [
        road_track(1, "car", (0, 0), (10, 0)),
        road_track(2, "car", (8, 0), (-10, 0)),
    ]

    assert evaluate_trajectory_cues(
        [short_track, road_track(2, "car", (50, 0), (-10, 0))],
        frame_id=0,
        timestamp_ms=0,
    ) == []
    assert evaluate_trajectory_cues(
        already_overlapping, frame_id=0, timestamp_ms=0
    ) == []
