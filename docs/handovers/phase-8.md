# Phase 8 Handover — Local Road Video and Trajectory Review MVP

Date: 2026-11-16

## Delivered

- Added a local-only catalog for two short, real road-scene clips. Each entry includes source, uploader attribution, license declaration, permitted local use, privacy status, and explicit annotation limits. Video files stay out of Git and are mounted read-only in the local Compose stack. A PowerShell helper downloads the clips and verifies their pinned SHA-256 checksums.
- Added deterministic image-plane trajectory-convergence evidence to sampled video and browser-camera results. The record contains track IDs, sample time, projected time to closest approach, margins, method, and an explicit `calibrated: false` marker. It is not a crash detector, risk probability, or safety instruction.
- Updated the operator workspace to keep video central and provide a readable cue review panel. The visual layer only surfaces a track pair after it appears in at least two analyzed samples within the grouping window; one-sample backend candidates remain in the developer JSONL. Live camera cues use the same repeated-pair rule. Cue styling is amber and static to communicate review status, not an emergency warning.
- Added backend unit coverage for cue geometry and the local benchmark catalog, plus frontend coverage for grouping and suppressing one-sample cues. CI now runs on all branch pushes as well as pull requests targeting `main`.
- Added `docs/MEASUREMENT_PLAN.md` with the labeled-footage, performance, warning-lead-time, and false-alert measurements needed before drawing effectiveness conclusions.

## Local smoke evidence

The Berlin motorway night clip (11.2 seconds) completed an 11-frame local CPU analysis at one sample per second. It produced 351 detections (346 cars, 3 trucks, 1 motorcycle, 1 person), 95 prototype track IDs, and 67 raw cue instances across 61 pairs. Six pairs appeared in at least two samples and qualified for the operator-facing review list.

This was a pipeline smoke run on unannotated footage. The counts are not precision/recall, track-quality, event-detection, or safety measurements. The high number of one-frame candidate pairs illustrates why the interface suppresses transient pairs; even repeated cues remain unvalidated and may be false alarms or misses.

## Footage provenance and handling

- Rainy road context clip: [Wikimedia source page](https://commons.wikimedia.org/wiki/File:Dest-20220814_170517.ogv), uploader `01x07x2022000` declares own work and CC0 1.0. The downloaded excerpt is not verified as an accident sample and has no event timestamp.
- Berlin night traffic clip: [Wikimedia source page](https://commons.wikimedia.org/wiki/File:Berlin_Bundesautobahn_100_2026-03-25_mov03.webm), uploader Lars Mueller declares own work and CC0 1.0. It is unlabeled traffic footage.
- [CC0 1.0 deed](https://creativecommons.org/publicdomain/zero/1.0/) describes the copyright dedication and notes that other rights, including privacy and publicity, may still apply. Both local clips remain marked `privacy_reviewed: false`; do not share them externally before review.

## Verification completed before push

- Backend Ruff passed; backend pytest: **19 passed** (53 deprecation warnings from current test dependencies/runtime).
- Frontend lint passed; Vitest: **17 passed**; TypeScript and Vite production build passed.
- Docker Compose configuration validated. Local API `/api/v1/health` reports healthy with database, CPU detector and retention available; frontend returned HTTP 200.
- The completed Berlin clip session is recorded locally as `fb896bb0-b2cb-4620-9c7d-a40ff81f6e57`. It processed 11 sampled frames. Its JSONL contains 351 detections and 351 track observations, 95 unique track IDs, 67 cue instances across 61 pairs, and six pairs appearing more than once. A trailing session summary record makes 12 JSONL records; it is not an additional analyzed frame.
- Both repositories are pushed on feature branches. The backend and frontend GitHub Actions workflows are configured to run for branch pushes; check runs should complete before any pull request merge. Do not merge into `main` as part of this handover.

## Not implemented or accepted

- Crash/incident detection or prediction, collision probability, warning lead-time validation, or accident prevention.
- RTSP or fixed-CCTV ingest, resilient camera reconnects, road-side alarm/buzzer control, or emergency-response integration.
- Calibrated speed/distance, validated vehicle counts, tracking accuracy, or representative Kigali/Rwanda footage.
- Privacy review, face/plate obscuring, external demo clearance, or a legal-compliance conclusion.
- Production readiness or investor claims beyond showing a local real-video analysis workflow.

See `docs/MEASUREMENT_PLAN.md` and `docs/PRODUCT_VISION.md` for gates toward a useful real-world MVP. No deployment, spending, DNS, or main-branch merge is part of this phase.
