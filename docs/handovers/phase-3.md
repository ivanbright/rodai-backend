# RodAI Phase 3 Handover ? First Real Detector

Date: 2026-11-14  
Status: **CPU detector integrated and exercised end to end on a local, licensed smoke sample. Representative Rwanda/Kigali validation and performance acceptance remain pending.**

## Delivered

- Selected `facebook/detr-resnet-50` after checking the model card, source and checkpoint metadata. Pinned checkpoint revision: `70120ba84d68ca1211e007c4fb61d0cd5424be54`. Provenance and the COCO/Flickr caveat are documented in [MODEL_PROVENANCE.md](../MODEL_PROVENANCE.md).
- Implemented CPU object detection for person, bicycle, motorcycle, car, bus and truck, with confidence and pixel-space `bbox_xyxy` coordinates.
- Uploaded-video processing writes per-frame detections to session JSONL; the frontend fetches results and synchronizes detection boxes/labels with video time.
- Browser camera uses the same detector and returns detections for the live overlay.
- Compose defaults to the pinned model. We split inference-only packages into `backend/requirements.inference.lock`; downloaded weights use the persistent RodAI data volume.

## Verification performed

- Backend: `pytest -q` ? 13 passed; Ruff check/format passed.
- Frontend: `npm run build`, `npm run lint`, and `npm test -- --run` passed (2 tests).
- Docker Compose: PostgreSQL healthy, API healthy, frontend running. The local API health endpoint reports database `available`, CPU selected, detector `available`, retention `available`, and zero failed deletions. Frontend root returned HTTP 200.
- Applied Alembic migration `0002_retention_camera_config` to the local Compose database.
- Real inference smoke: uploaded a 14-frame, 720?1280, 2 FPS, 7-second derivative from the documented Pexels road clip. The API completed inference on all 14 frames with 0 dropped frames and returned 163 total detections: person 75, car 35, truck 21, motorcycle 18, bicycle 13, bus 1. Source and test derivative are in ignored `.temp/samples/`; neither is committed. The test output is `.temp/samples/rodai-detection-smoke.jsonl`.
- This smoke run proves the inference and result pipeline execute. It is **not** an accuracy study or a measured performance benchmark; no reliable latency, throughput, CPU/RAM profile or target has been accepted.

## Run the local demo

Docker currently maps ports 8000 and 5432 in another project, so this workspace is running with the local Compose override: API `http://localhost:8001`, UI `http://localhost:5173`. Health: `http://localhost:8001/api/v1/health`. The override is `docker-compose.local.yml` and replaces only host port mappings.

From `D:\rodai` in PowerShell, run:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build rodai-db rodai-api rodai-frontend
docker compose -f docker-compose.yml -f docker-compose.local.yml ps
```

Then open `http://localhost:5173`, choose an MP4, MOV, MKV, WebM or AVI video, press **Process video**, and wait for completion. Play the preview to see boxes and labels synchronized to playback; session history contains the JSONL results. The first run downloads the pinned model checkpoint. This local smoke sample is at `.temp/samples/cars-motorcycles-pexels-20669311-demo.avi`; its source/licensing and privacy notes are in [sample-video-manifest.md](../sample-video-manifest.md). It is not committed.

## Limits and remaining acceptance

- This detects objects in sampled frames. It does not track identities, predict collisions, classify accidents, or provide safety monitoring. Do not use it to make road-safety decisions.
- The Pexels video is a private local pipeline smoke test, not representative Kigali footage. Source frames include pedestrians and small visible plates; do not share the footage or outputs externally without privacy review and plate blurring. Owner-provided footage with documented rights and required metadata remains a prerequisite for representative acceptance.
- Hardware details are not yet confirmed. Measure throughput, per-frame latency, CPU/RAM and drop rate on the development hardware using representative permissioned footage before setting performance targets or permitting higher capture resolutions.
- The React overlay path is implemented and result retrieval was observed in API logs, but the UI could not be screenshot-verified in this session because the computer/browser-control service was unavailable. Recheck the visible overlay during the next interactive review.
- Face/plate blurring, tracking, event detection, model evaluation on a labeled target sample, deployment, authentication and product design from the owner?s references remain future work. Phase 5 design references must be reviewed before design implementation.
- Model licensing notes are technical provenance, not a legal determination. See [MODEL_PROVENANCE.md](../MODEL_PROVENANCE.md).

## Next step: simulation lab

The first controlled-scenario lab is recorded in `phase-4.md`. It demonstrates scripted conflict scenarios and a rule-based intervention flow independently of camera detection. The lab is not accident-prediction model evidence.
