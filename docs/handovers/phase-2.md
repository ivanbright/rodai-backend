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
