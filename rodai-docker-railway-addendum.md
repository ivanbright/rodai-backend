# RodAI — DOCKER, DATABASE AND RAILWAY ADDENDUM (v2.1)

**Append this to `rodai-master-prompt.md` as Section 22. Where it conflicts with earlier sections, this addendum wins (listed in 22.1).**

---

## 22. CONTAINERISATION AND DEPLOYMENT

### 22.1 Changes to earlier sections

| Earlier rule | New rule |
|---|---|
| 4.8 "Local-first, runs on the developer machine" | **Local-first inference, container-first packaging.** Inference never uses paid AI APIs, but RodAI is packaged in Docker and runs identically on the owner's machine and on Railway. |
| 4.3 / 6.4 "No database unless justified" | **A database is now justified** (deployed multi-session use, persistence across container restarts). Use PostgreSQL. See 22.5. |
| 16.5 "No authentication; bind to localhost" | **Authentication is required** once RodAI is on a public domain. See 22.9. |
| 12.6 Config system | Configuration is **environment-variable driven** (12-factor). See 22.4. |
| 13.1 Hardware: CPU/CUDA | **Production target is CPU-only.** See 22.7. |
| 16.8 Performance targets | Targets are set **per environment** (local vs Railway) after benchmarking in Phase 3. |

### 22.2 Deployment target (decided; do not re-litigate)
- Hosting: **Railway**, deployed from a Git repository using a **Dockerfile** (not Nixpacks auto-detection).
- Domain: the owner's own domain mapped to the Railway service via Railway's custom-domain feature (DNS CNAME at the owner's DNS provider; TLS provided by the platform). **[OWNER TO CONFIRM: domain name and DNS provider.]**
- Browser camera access (`getUserMedia`) requires HTTPS, so the deployed domain must be served over HTTPS, and the WebSocket must use `wss://`.
- **Verify current Railway capabilities, limits and pricing against Railway's documentation in Phase 0.** Do not rely on memory for: memory/CPU limits per plan, request timeouts, upload size limits, volume support and size, WebSocket behaviour, GPU availability, build timeouts.

### 22.3 Container architecture

**Services (Railway project):**
1. `rodai-app` — one container: FastAPI backend **and** the built frontend static files served by the backend. *Default recommendation:* one origin, one domain, no CORS problems, one deployment. Alternative: a separate frontend service — only if the owner wants independent scaling or a CDN. Present the trade-off in Phase 0 and record the decision.
2. `postgres` — Railway-managed PostgreSQL.
3. **Volume** attached to `rodai-app` for uploads, exports and model weights (container disk is ephemeral and is wiped on every redeploy).

No Redis, no queue, no worker service unless Phase 0 proves a need (justify in `DECISIONS.md`).

**Local development uses Docker Compose** with: `backend`, `frontend` (Vite dev server with hot reload), `postgres`. One command starts everything: `docker compose up`. A second command runs tests inside containers.

### 22.4 Configuration rules
- All configuration comes from environment variables, validated at startup with Pydantic Settings. The app MUST refuse to start with a clear error if a required variable is missing or invalid.
- Provide `.env.example` listing **every** variable with description and a safe default or placeholder. Never commit `.env` or secrets.
- Minimum variable set (extend as needed, keep names prefixed `RODAI_`):
  `RODAI_ENV` (`local` | `staging` | `production`), `PORT` (supplied by Railway; bind `0.0.0.0:$PORT`), `DATABASE_URL`, `RODAI_DATA_DIR` (volume mount path), `RODAI_MODEL_DIR`, `RODAI_ALLOWED_ORIGINS`, `RODAI_SECRET_KEY`, `RODAI_MAX_UPLOAD_MB`, `RODAI_MAX_VIDEO_SECONDS`, `RODAI_MAX_CONCURRENT_SESSIONS`, `RODAI_DEVICE` (`auto` | `cpu` | `cuda`), `RODAI_DETECTION_MODEL`, `RODAI_INFERENCE_IMGSZ`, `RODAI_LOG_LEVEL`.
- Behaviour differences between environments come **only** from configuration, never from code branches on hostnames.

### 22.5 Database
- **PostgreSQL**, accessed through SQLAlchemy 2.x with **Alembic** migrations. Migrations are versioned, reversible where possible, and run as an explicit step (not on every app start without a lock).
- **Use the same engine locally and in production** (Postgres via Compose) to avoid "works on SQLite, fails on Postgres" drift. Present this to the owner as the default; SQLite locally is allowed only if the owner prefers simplicity and accepts the drift risk.
- Candidate tables (confirm in Phase 0; create only what the current phase needs): `users`, `sources`, `sessions`, `session_results` (metadata + path to exported JSONL, not per-frame rows), `events`, `models` (registry), later `datasets`, `experiments`.
- **Do not store per-frame detections or video blobs in Postgres.** Per-frame results go to JSONL files on the volume; the database holds metadata and indexes. Justify any exception.
- Database access goes through a repository/service layer, never directly from route handlers.
- Connection pooling configured explicitly; the app handles database unavailability with a clear health status, not a crash.

### 22.6 Dockerfile standards

**Backend image:**
- Multi-stage build; base `python:3.12-slim` pinned to a specific tag (record the digest in the handover).
- Install **CPU-only PyTorch** from the official CPU wheel index; use **`opencv-python-headless`** (not `opencv-python`). Do not install CUDA packages in the production image.
- Install system libraries only if required (e.g. `ffmpeg`, `libgl1`/`libglib2.0-0` equivalents); justify each.
- Install from a **lockfile** with pinned versions; no `latest` tags anywhere.
- Run as a **non-root user**; no secrets baked into layers; no model weights committed into the Git repo.
- Copy dependency manifests first, then source, to maximise layer caching.
- `HEALTHCHECK` / Railway healthcheck path: `GET /api/v1/health` returning real status (database reachable, model state, device, free volume space).
- Handle `SIGTERM` for graceful shutdown: stop active sessions, flush exports, close DB pool, within a stated timeout.
- Logs go to **stdout/stderr** as structured JSON; do not write log files inside the container.

**Frontend image / stage:**
- Build stage: Node (pinned LTS) runs `npm ci` and `npm run build`; only the built `dist/` is copied into the final backend image (or an nginx image if a separate service is chosen).
- Environment-specific values are not baked in at build time unless unavoidable; prefer runtime config (e.g. same-origin `/api` and `wss://<host>/ws`).

**Repository hygiene:** `.dockerignore` excluding `node_modules`, `.git`, datasets, videos, checkpoints, `.env`, caches, tests artefacts. Target a small final image; record the image size in each handover and justify growth over the previous phase.

### 22.7 Resource and performance constraints (CPU-only production)
- Assume **no GPU on Railway** (verify in Phase 0). Production inference is CPU inference.
- Therefore: default to the smallest detector (e.g. nano size), reduced input size, frame sampling/skipping, and a conservative live-preview rate. These are **configuration**, not code changes.
- **Offline video processing runs as a background task with real progress reporting**, so HTTP requests never wait for it and are not killed by proxy timeouts. Chunked or streamed upload for large files; enforce `RODAI_MAX_UPLOAD_MB` and `RODAI_MAX_VIDEO_SECONDS`.
- Run **one Uvicorn worker** initially (model memory and in-process session state), and state this limit explicitly. Multi-worker requires moving session state out of process and needs approval.
- Limit concurrent sessions (`RODAI_MAX_CONCURRENT_SESSIONS`, default 1–2); reject extras with a clear message.
- Browser-camera live mode sends frames over the internet: define bandwidth and latency budgets (frame size, JPEG quality, send rate) and measure end-to-end latency on the deployed domain, not only locally. If latency is unacceptable, report it honestly and propose options (lower rate, lower resolution, offline mode only for the public deployment).
- **Model weights:** not in Git, not rebuilt each deploy. Download once into the volume (documented script/startup step with checksum verification), or bake into the image if size permits — decide and justify in Phase 0.
- **Training and heavy experiments never run on Railway.** Train locally or on a GPU service (e.g. Colab/Kaggle/rented GPU), then publish versioned weights to the volume. State this in the docs.

### 22.8 Environments and release flow
- Three environments: **local** (Compose), **staging** (a Railway environment, optional but recommended), **production** (Railway + custom domain).
- Deploy from Git: merging to the main branch triggers a Railway build. Tag every approved phase (`rodai-phase-N`).
- **Early deployment (new Phase 1B, below):** deploy the skeleton to Railway as soon as it exists, so deployment problems are found in Phase 1, not Phase 8.
- Every phase's acceptance criteria now include: **builds in Docker, runs via Compose, and (from Phase 1B) deploys to Railway with a passing health check.**
- Provide a documented rollback procedure (redeploy previous Railway deployment; database migration downgrade notes).

### 22.9 Security for a public deployment
- **Authentication required.** Start with the simplest approach that is real: owner-managed accounts or invite-only login with hashed passwords (Argon2/bcrypt) and secure session cookies or short-lived tokens. No hard-coded credentials. Propose in Phase 0; wait for approval. Do not add third-party identity providers without approval.
- Protect all API routes and the WebSocket (authenticate on connect; validate `Origin`).
- **Rate limiting** and per-user upload quotas; reject oversized or over-long videos before heavy processing.
- Strict CORS/Origin allow-list from `RODAI_ALLOWED_ORIGINS`; security headers; no debug mode or stack traces in production responses.
- Uploaded files: content-type and magic-byte validation, randomised storage names, stored only under `RODAI_DATA_DIR`, never executed, never served from a path the user can control.
- **Privacy on a public host:** uploaded road video may contain faces and number plates. Define retention (e.g. automatic deletion of uploads after N days — configurable), a delete-my-data path, and a clear privacy notice on the site. **[OWNER TO CONFIRM retention period and applicable data-protection rules.]**
- **Licence check (now more important):** Ultralytics YOLO is AGPL-3.0; hosting it as a network service can trigger source-availability obligations. Resolve in Phase 0 (accept AGPL and publish source, buy a commercial licence, or use a permissively licensed detector). Do not deploy publicly before this is decided.
- Secrets live only in Railway environment variables. Provide a documented procedure to rotate `RODAI_SECRET_KEY` and database credentials.

### 22.10 Observability
- Structured JSON logs with request ID and session ID.
- `/api/v1/health` (liveness + dependencies) and `/api/v1/system` (device, model state, queue depth, memory, disk) — real values only.
- Track and expose: dropped frames, inference latency, active sessions, volume usage. Alert-worthy conditions (volume nearly full, model failed to load, DB unreachable) surface as a clear status, not silent failure.

### 22.11 Revised and added phases

**PHASE 1 — FOUNDATION (revised)  ⛔ approval required**
Everything in Phase 1 **plus**: backend and frontend Dockerfiles, `docker-compose.yml`, `.dockerignore`, `.env.example`, Pydantic Settings, Postgres container, Alembic initialised with a first migration, `/api/v1/health` reporting database, device and volume status, container tests.
*Accept:* `docker compose up` brings up the full stack from a clean clone; health shows real database, device and config state; tests pass inside containers; image sizes recorded; no secrets in the repo or image.

**PHASE 1B — FIRST RAILWAY DEPLOYMENT  ⛔ approval required** (new)
Deploy the Phase 1 skeleton to Railway: Dockerfile build, Postgres service, volume, environment variables, healthcheck, custom domain with HTTPS, `wss://` connectivity test, authentication skeleton.
*Accept:* the owner opens `https://<their-domain>`, logs in, sees a real health status from the deployed backend, and a WebSocket echo test works over `wss`; redeploy keeps volume data; rollback tested once; the deployment guide in `docs/deployment.md` was followed from scratch by a clean checkout.

**Later phases:** each handover adds container build result, image size, deployed health check result, and (from Phase 3) CPU benchmark numbers **on Railway**, not just locally.

### 22.12 New documentation required
`docs/deployment.md` (Railway setup step by step, environment variables, domain/DNS, volume, database, rollback), `docs/docker.md` (images, Compose, commands), `docs/security.md`, `docs/privacy.md` (retention and data handling), `docs/licences.md`.

### 22.13 New questions for the owner (add to Phase 0 output)
1. Domain name, DNS provider, and subdomain to use (e.g. `rodai.<domain>`).
2. Railway plan and monthly budget (affects CPU/RAM, model size, concurrent sessions).
3. Who will use the deployed site: only you, invited testers, or the public? (Determines auth and quota design.)
4. Single service (backend serves frontend) or separate frontend service?
5. Local database: Postgres in Compose (recommended) or SQLite?
6. Licence decision for the detector (AGPL, commercial, or alternative).
7. Upload retention period and acceptable maximum video length and size.
8. Is live browser-camera mode required on the public deployment, or is uploaded-video mode enough for the first public release?
