# RodAI Phase 2 Handover — Video and Session Pipeline

Date: 2026-11-14  
Status: **Implemented and locally verified.** This phase performs video decoding and frame transport only; it does not run detector inference.

## Delivered

- Bounded local video upload with allowed container validation, duration checks, progress, session status and pause/resume/stop controls.
- Browser camera streaming using WebSocket, frame IDs, capture timestamps and dropped-frame accounting.
- Frame-aligned JSONL session output with schema version, dimensions, timing and explicit `inference: not-run` records.
- Session list/detail, result download and deletion. Raw uploaded video is temporary and cleaned after processing; exported session JSONL remains until the user deletes the session.
- UI video preview, upload/session controls, session history, camera preview and JSONL download.
- Interrupted active sessions are marked failed on API startup and temporary uploads are cleaned.

## Verification

- Backend: `pytest -q` — 9 passed; `ruff check rodai tests` — passed.
- Frontend: `npm run build` — passed; `npm run lint` — passed; `npm run test -- --run` — 2 passed.
- Compose: PostgreSQL healthy, API healthy, Vite frontend running; frontend root returns HTTP 200 and `/api/v1/health` proxy reports healthy with database available.
- Docker API image rebuilt and containers recreated. A synthetic three-frame AVI upload against the container returned completed, three processed frames and four JSONL records (three frames plus summary); deletion returned 204.
- SQLite-backed tests cover unsupported/invalid videos, JSONL output, session deletion, controls and WebSocket frame handling/drop accounting.

## Known limitations

- No detector, inference, detections or tracking are present. Detector status remains unavailable by design until Phase 3.
- Browser camera requires HTTPS or localhost browser permission. WebSocket transport is local-only as currently configured and has not been independently tested through an external reverse proxy.
- Local frontend `npm ci` reports 14 advisories (2 low, 9 moderate, 1 high, 2 critical). Registry TLS validation prevented retrieving audit details; resolve before deployment.
- Target camera context, sample footage and permissions, hardware inventory and model licensing remain owner decisions for detector selection and validation.

## Run and inspect

- Start: `docker compose up --build` from repository root.
- UI: `http://localhost:5173`; API health: `http://localhost:8000/api/v1/health`.
- API endpoints are under `/api/v1/sessions`; WebSocket route is `/api/v1/sessions/ws/{session_id}`.
- See `docs/PROJECT_STATE.md` for current phase and outstanding decisions.

## Owner-approved conformance closeout — 2026-11-14

The owner approved Phase 0 and directed implementation to continue. This update supersedes the earlier status and limitation notes where noted below.

- Configurable expiry policies are implemented: upload 7 days, result/session history 30 days, stored download copies 7 days, each configurable with validated settings. An hourly sweep deletes files before records, writes an audit result for each attempt, and retains failures for retry. Model/checkpoint paths cannot be registered for automatic expiry.
- Existing database upgrade: run `docker compose run --rm rodai-api alembic upgrade head` to apply `0002_retention_camera_config`.
- Browser camera defaults to 1280×720, offers 960×540 and 640×360, configures JPEG quality 0.50–0.95 (default 0.82), downscales client frames, validates size/quality server-side, and acknowledges the effective configuration.
- Live stop messages include any final client drop count. Drop totals appear in session responses, results, and the live session card.
- The one-active-session rule remains enforced and returns HTTP 409 on collision.
- Automated acceptance: `pytest -q` — 13 passed, including synthetic ordered video, camera settings negotiation/invalid values, one-session conflict, trailing drop totals, expiration boundary/retry/idempotency and model-expiry protection. Ruff passed. Frontend build and ESLint passed; see latest Vitest result in Phase 3 handover.
- Runtime closeout: Docker became available later in this continuation. Migration `0002_retention_camera_config` was applied to the local Compose database; PostgreSQL and API report healthy. The current runtime evidence and port override are recorded in `phase-3.md`.
