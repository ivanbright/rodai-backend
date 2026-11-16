# RodAI MVP measurement plan

Updated: 2026-11-15

## Purpose

Measure whether RodAI can turn camera video into useful, reviewable evidence for an operator. The current prototype detects a limited set of road users and emits an experimental image-plane trajectory-convergence cue. It does not detect or predict accidents, provide calibrated speed, or prevent collisions. A cue is not a probability or an instruction to intervene.

## What is available to measure now

- Detector outputs: class, confidence and bounding box at the selected analysis sampling rate.
- Prototype tracks: track IDs, image-plane centers, trails and pixel-per-second motion.
- Experimental backend cues: candidate pairs whose constant-velocity projections approach within their current bounding-box dimensions over a three-second image-plane horizon.
- Runtime observations: clip duration, analyzed frames, elapsed processing time, selected device, memory, CPU and dropped live-camera preview frames.

The two downloaded CC0 road-scene clips are workflow demonstrations only. Neither has a trusted risk-event label or timestamp, and their privacy review is pending. They cannot be used to calculate accident-warning accuracy or target-region performance.

## Annotation needed for a meaningful risk evaluation

For each permissioned clip, record source and rights, camera identity/viewpoint, capture date/context, resolution, frame rate, weather/light, and any privacy treatment. Reviewers must label:

1. Road users and boxes at a documented sampling interval, including visible/occluded status.
2. Track identities for the labeled interval, with ambiguous identity changes marked rather than guessed.
3. Each conflict, near-miss or incident using a written definition, its event onset and end, and the earliest timestamp at which a human reviewer can identify the hazardous interaction.
4. Whether the interaction is in view and whether the clip has enough pre-event lead-in to assess an early cue.

Use two independent reviewers for risk-event boundaries and adjudicate disagreements. Keep the annotation source and reviewer version with each evaluation run. Split by source clip, camera and time before tuning; adjacent frames from one clip must never cross training, tuning and held-out partitions.

## Report for every run

| Area | Measures |
| --- | --- |
| Road-user detection | Per-class precision, recall, AP where boxes are labeled, confidence threshold, analyzed FPS, and missed/false detections by lighting and object size. |
| Tracking | IDF1 or HOTA where annotations support it, ID switches, fragmentation, and track coverage duration. |
| Risk-review cues | Event-level precision and recall, false cues per camera-hour, missed events, time from first cue to annotated event onset, and fraction of events with a cue before onset. Report cue availability and latency separately. |
| Runtime | Wall-clock processing time, effective analyzed FPS, CPU and peak RAM on the inspected development hardware, plus dropped preview frames for live camera. |
| Operator utility | Reviewer agreement, time to find evidence, whether the cue explanation is understandable, and false-alarm burden in a blinded walkthrough. |

For the trajectory cue, preserve raw event counts and the event-matching rule. A candidate only counts as a true positive when its track pair and time window correspond to the manually annotated interaction. Publish false positives and misses alongside any aggregate score. Do not tune against the held-out set.

## Acceptance gate

No numerical success threshold is asserted yet. First collect hardware details and a permissioned, representative labeled set that includes normal traffic, near-conflicts and incidents across day/night and weather conditions. Use those measurements and a reviewer workload discussion to set minimum thresholds with the owner. Then run a frozen configuration on a held-out set and report the raw sample size, uncertainty, failure cases and model/runtime versions. The MVP may be shown before this gate only as a local perception and evidence-review prototype, with the experimental cue clearly labeled.

No audible roadside buzzer, automated signal action, emergency dispatch or public safety claim is part of this acceptance gate. Those actions need separate authority, safety and human-factors review after the cue's false-alarm rate and lead time have been measured.
