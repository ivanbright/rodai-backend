# RodAI Project State

Updated: 2026-11-16

## Current MVP

RodAI is a local-first road-video analysis prototype. It accepts an uploaded clip, a locally registered road demo, or a browser camera; runs sampled frames through a CPU DETR detector; tracks objects between samples; and shows detections and trails over the video. It can also report exploratory line crossings and image-plane trajectory review cues.

The frontend is centered on an in-page video workspace. It keeps the annotated video visible, provides readable track and cue summaries, and tucks raw JSONL under developer details. Repeated trajectory pairs are shown to operators only after appearing in at least two nearby analyzed samples. One-off candidates remain available in JSONL. The repeated-sample gate reduces visual noise; it does not validate cue accuracy.

Two short, unannotated open road-scene demos are available in the local library. Their files are ignored by Git and mounted read-only for local use. Source pages contain uploader-declared CC0 notices; privacy review is still pending, so keep the footage private and review faces/plates before sharing. Neither clip is a verified accident example or Kigali/Rwanda evaluation footage.

## Measured smoke run

The 11.2-second Berlin night-traffic clip completed a local CPU smoke run at one analyzed frame per second: 11 sampled frames, 351 detections (346 cars, 3 trucks, 1 motorcycle and 1 person), and 95 prototype track IDs. The backend emitted 67 trajectory-cue instances across 61 distinct pairs. Only six pairs appeared in at least two samples and qualify for the operator review view. This unannotated clip provides no ground truth; these counts show pipeline operation and cue noise, not accuracy, near-miss detection, or safety performance.

## Implemented foundation

- **Phase 2:** Configurable retention, camera capture settings, and one-session concurrency requirements are implemented. Retention behavior is auditable and defaults are documented as technical settings, not a legal-compliance claim.
- **Phase 3:** CPU DETR detector integrated. It identifies supported object classes; it does not identify crashes or predict them.
- **Phase 4:** The scripted SVG simulation was removed from the frontend because it did not exercise real video. Historic details and limitations remain in `docs/handovers/phase-4.md`.
- **Phase 5:** Prototype online tracking, image-plane trails, and pixels-per-second motion for uploaded and browser-camera sessions. Track identity stability and physical speed are unvalidated.
- **Phase 6:** Sampled uploads, progress/errors, annotated browser WebM export, and readable in-page results. Raw JSONL is secondary developer data.
- **Phase 7:** Exploratory virtual line crossings and browser-local line profiles for matching aspect ratios. They do not calibrate speed.
- **Phase 8:** Local road-demo library, deterministic image-plane trajectory cues, in-place cue review, conservative repeated-pair display, expanded tests, and branch-triggered CI. See `docs/handovers/phase-8.md`.

## Local operation

PostgreSQL, API, and frontend run through Docker Compose. The API uses host port 8001 in this workspace because host port 8000 is occupied. The CPU model loads on first analysis. Start the local stack with:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Local demo videos are downloaded and checksum-verified with `scripts/download-open-road-demos.ps1`. They are intentionally excluded from Git and container images.

## Verification and limits

Backend Ruff and pytest, frontend lint/tests/production build, Compose configuration, API health, and a real local video smoke run are checked before this delivery. Detailed results are in the Phase 8 handover.

Still outstanding: labeled and permissioned footage for evaluation; detection/tracking/cue metrics and false-alert analysis; reliable camera ingestion such as RTSP; calibrated speed; operator alert workflows; privacy review and face/plate treatment; representative Kigali/Rwanda footage; and measured hardware performance. No feature currently predicts or prevents accidents, triggers a road-side buzzer, or supports operational safety decisions. Planned work is not counted as implemented.

See `docs/PRODUCT_VISION.md`, `docs/MEASUREMENT_PLAN.md`, `docs/DECISIONS.md`, and `docs/QUESTIONS.md` for direction, evaluation requirements, and owner decisions.
