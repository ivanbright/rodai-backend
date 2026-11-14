# RodAI Phase 7 Handover — Real-Video Movement Measurement

Date: 2026-11-14  
Status: **A virtual counting line reports sampled track crossings and direction for uploaded footage. Named line profiles can be saved in the current browser and reused on matching-aspect-ratio video. This remains an exploratory measurement tool, not a validated traffic counter.**

## Delivered

- Added a line-crossing utility that operates on the current session's actual tracker output and timestamps.
- Added a drag-to-draw line tool on the annotated uploaded-video viewer. The oriented line is visible during playback and included in annotated-video export.
- Added total, negative-to-positive, and positive-to-negative crossing counts plus a short recent-event list with track ID, class, direction, and sample timestamp.
- Added a deadband around the line to reduce counts caused by small image-space jitter, finite segment intersection checks, and one crossing maximum per session-local track ID.
- Added deterministic tests for both directions, finite line bounds, jitter deadband, and degenerate line geometry.
- Added named fixed-view profiles stored in browser local storage. A profile stores normalized line geometry and reference video dimensions, can be applied to another video with a matching aspect ratio, and can be deleted from that browser.
- Added format validation and defensive handling for corrupted or unsupported profile data, duplicate names, profile storage failures, and incompatible aspect ratios.

## How to use it

1. Process an uploaded road video and wait for analysis to finish.
2. Choose **Add traffic count line** under the video.
3. Drag across a road segment in the video. The endpoints are labelled A and B; the reported directions are the negative and positive sides relative to that oriented line.
4. Review observed crossings below the session summary. Redraw or clear the line as needed. Include the line in an annotated WebM export if desired.
5. To reuse the line for the same fixed view, enter a profile name and choose **Save camera profile**. On a later video, choose the saved view and **Apply line**, then verify that the overlay still matches the road before interpreting its counts.

## Limits

- Counts use only analyzed samples. At low analysis sampling rates, a short crossing may occur between samples and be missed.
- Counts depend on the prototype tracker. A track ID switch may double-count one road user; a fragmented or lost track may miss one.
- Profiles are stored only in the current browser. They do not sync between users/devices or prove that a later clip came from the same camera; an operator must verify the overlay each time.
- Profiles only apply to matching aspect ratios. A matching ratio does not prove that framing, zoom, crop, or camera position stayed the same.
- The system does not convert pixels to metres or km/h. No physical speed is shown or inferred by this feature.
- No representative, permissioned Rwanda/Kigali footage or manually reviewed ground truth was available for accuracy acceptance. Do not present these counts as validated traffic statistics.

## Verification

- Frontend ESLint passed.
- Vitest: 11 tests passed, including 4 movement-crossing cases and 5 camera-profile storage/geometry cases.
- TypeScript production build passed.
- Utility tests use deterministic local inputs. They validate line geometry/profile compatibility only; they do not establish detector or tracker accuracy.

## Next acceptance work

- Add explicit camera identity/configuration and a controlled road-plane calibration workflow.
- Evaluate missed and duplicate crossings against manually reviewed annotations on permissioned footage, across analysis rates and track fragmentation cases.
- Show physical speed or distance only after calibration can be independently checked against known distances and timestamps, with uncertainty reported.
- Continue to keep CCTV/RTSP ingest and incident-risk alerts as separate milestones with their own security, performance, and labeled-footage gates.
