# RodAI Phase 7 Handover — Real-Video Movement Measurement

Date: 2026-11-14  
Status: **A session-local virtual counting line now reports sampled track crossings and direction for uploaded footage. It is an exploratory measurement tool, not a validated traffic counter.**

## Delivered

- Added a line-crossing utility that operates on the current session's actual tracker output and timestamps.
- Added a drag-to-draw line tool on the annotated uploaded-video viewer. The oriented line is visible during playback and included in annotated-video export.
- Added total, negative-to-positive, and positive-to-negative crossing counts plus a short recent-event list with track ID, class, direction, and sample timestamp.
- Added a deadband around the line to reduce counts caused by small image-space jitter, finite segment intersection checks, and one crossing maximum per session-local track ID.
- Added deterministic tests for both directions, finite line bounds, jitter deadband, and degenerate line geometry.

## How to use it

1. Process an uploaded road video and wait for analysis to finish.
2. Choose **Add traffic count line** under the video.
3. Drag across a road segment in the video. The endpoints are labelled A and B; the reported directions are the negative and positive sides relative to that oriented line.
4. Review observed crossings below the session summary. Redraw or clear the line as needed. Include the line in an annotated WebM export if desired.

## Limits

- Counts use only analyzed samples. At low analysis sampling rates, a short crossing may occur between samples and be missed.
- Counts depend on the prototype tracker. A track ID switch may double-count one road user; a fragmented or lost track may miss one.
- The line exists only for the currently open browser session and is not saved as a camera profile.
- The system does not convert pixels to metres or km/h. No physical speed is shown or inferred by this feature.
- No representative, permissioned Rwanda/Kigali footage or manually reviewed ground truth was available for accuracy acceptance. Do not present these counts as validated traffic statistics.

## Verification

- Frontend ESLint passed.
- Vitest: 6 tests passed, including 4 movement-measurement geometry cases.
- TypeScript production build passed.
- The movement utility tests use deterministic synthetic track paths. They validate the crossing geometry only; they do not establish detector or tracker accuracy.

## Next acceptance work

- Persist counting lines as camera profiles with a controlled calibration workflow.
- Evaluate missed and duplicate crossings against manually reviewed annotations on permissioned footage, across analysis rates and track fragmentation cases.
- Add road-plane calibration and speed uncertainty only after calibration can be independently checked against known distances and timestamps.
- Continue to keep CCTV/RTSP ingest and incident-risk alerts as separate milestones with their own security, performance, and labeled-footage gates.
