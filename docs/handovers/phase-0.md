# RodAI Phase 0 Handover — Inspection and Architecture

Date: 2026-11-12  
Status: **Report prepared; Phase 0 is not approved or complete.** No application code was written and no packages were installed.

Update: Owner supplied `rodai-docker-railway-addendum.md` and authorized work to start. This revision incorporates its requirements. It does not resolve owner-only details such as the Railway plan/budget, domain, intended users, retention, or detector licence.

## 1. What was implemented

Phase 0 inspection and planning only. Created project state, decision, assumption and question documents plus this handover. This is documentation, not application implementation.

## 2. Files created/changed

- `docs/PROJECT_STATE.md`
- `docs/DECISIONS.md`
- `docs/ASSUMPTIONS.md`
- `docs/QUESTIONS.md`
- `docs/handovers/phase-0.md`
- `CHANGELOG.md`

## 3. Dependencies installed

None.

## 4–5. What was checked and actual results

Commands run in the workspace:

```text
python --version       -> Python 3.13.2
node --version         -> v22.13.0
git --version          -> git version 2.49.0.windows.1
```

Additional inspection results:

- .NET reported `Win32NT`, kernel version `10.0.26300.0`; this does not establish the Windows edition.
- `systeminfo.exe` returned `ERROR: Access denied`.
- `Get-CimInstance` for OS, CPU and video controllers returned `Access denied`.
- `nvidia-smi` was not found.
- CPU count visible to this process: 20 logical processors; physical CPU model and core count are unknown.
- RAM and GPU/VRAM/CUDA are unknown. Disk inventory was not available from the restricted shell.
- Before documentation creation, the workspace contained only `rodai-master-prompt.md`; no source code, docs, sample videos or design references existed.
- No tests or application commands exist to run.

## 6. Proposed architecture

Local-first modular monolith. FastAPI owns sessions, ingestion, inference, tracking, analysis, exports, status and WebSockets. React, TypeScript, Vite and Canvas provide upload/camera controls, video preview and frame-aligned overlays. One shared backend pipeline handles uploaded and camera frames, with distinct offline and live-preview queue policies. Bind to localhost by default. Keep modules replaceable without introducing microservices or a database unless a confirmed requirement justifies one.

### Data flow

Browser upload or `getUserMedia` → frame/source validation → session manager → preprocessing → detection → tracking → movement history → optional analysis → structured session result/event → `rodai.v1` WebSocket → viewer overlay matched by frame ID/timestamp. Export results as JSONL; annotated video is optional pending owner decision.

### Input, session and transport proposal

- Offline uploaded video: preserve order and process every selected frame; report real progress; do not silently drop.
- Live browser camera: bounded queue, newest-frame-wins; count and report dropped frames.
- Proposed initial concurrency: one active session; reject or clearly report a second start until the first ends.
- Proposed browser frame transport: binary WebSocket JPEG with a client capture timestamp and monotonic frame ID. Backend echoes IDs/timestamps. This is a proposal requiring owner confirmation and Phase 2 alignment testing.
- Proposed result messages use JSON and `rodai.v1`, carrying message type, session/frame IDs, timestamps, status, implemented detections/tracks/events, and structured errors. Define ordering, heartbeat, reconnect and malformed-message handling before Phase 2.
- Persist JSONL results/config/model metadata to local files by default. No SQLite until cross-restart searchable history is required.

### Export schema proposal

One JSONL session manifest/header with schema and protocol version, session/source IDs and type, frame dimensions, timestamps policy, processing mode, configuration, and model identifiers/versions; then one record per processed frame containing frame ID/time, actual detections and track outputs (empty arrays when none), implemented movement/risk records, and processing errors/status. End with a summary record including processed/dropped frame counts and termination status. Version the schema; never infer missing outputs. Annotated video can be added only if approved.

### API and WebSocket proposal

Version HTTP routes under `/api/v1`: health/system, sources, sessions, models, events and exports as each becomes implemented. OpenAPI is generated from actual schemas. `rodai.v1` WebSocket messages have explicit envelope and schemas; session lifecycle and error message types are documented before Phase 2. Health reports actual runtime/device/model state and does not return fabricated readiness.

## 7. Environment and model assessment

- Detected host OS family is Windows, but exact edition/build identity, CPU, memory, GPU and free space require owner or admin-enabled inventory.
- Installed Python 3.13.2 is a compatibility risk: the current PyTorch Windows installation page says Python 3.9–3.12 is supported. Proposal: use Python 3.12 in an isolated project environment, verify exact current PyTorch/vision wheels and detector package compatibility before pinning. Do not use Python 3.13 for the ML environment unless official compatibility changes and is checked.
- No NVIDIA GPU was established; absence of `nvidia-smi` is not proof there is no GPU. CPU fallback is mandatory. No FPS or practical real-time performance claim is justified before hardware and footage benchmarks.
- Detector proposal: compare lightweight and larger candidate sizes in Phase 3 on the actual machine and owner footage. Confirm actual weight class map, model card and weight licence before download/use. No weights selected or downloaded.
- Ultralytics is the convenient YOLO route but AGPL-3.0 obligations or its separate Enterprise licence affect distribution. The original RT-DETR repository identifies Apache-2.0, but code and each pretrained weight/checkpoint must be licensed and reviewed separately. Neither is selected.
- ByteTrack is a candidate tracker; verify the exact repository, dependencies and applicable licences before adding it.

## 8. Proposed dependencies and tooling

These are candidates only; exact versions and licences must be checked and pinned in Phase 1 after decisions. Python: FastAPI, Uvicorn, Pydantic, PyYAML, OpenCV, PyTorch/torchvision, detector runtime, and a tracker if needed. Frontend: React, TypeScript, Vite, Tailwind CSS, and a WebSocket/client layer using browser APIs. Development: Ruff, mypy or Pyright, pytest, ESLint, Prettier, Vitest, and Playwright. Each package adds maintenance and install size; PyTorch/OpenCV/model weights are the largest footprint. Avoid adding both alternative frameworks without a demonstrated need. Do not install anything in Phase 0.

## 9. Licensing, footage, privacy and ethical position

- No datasets, sample videos, weights or third-party code are in the workspace. Dataset/video licence and permission cannot be assessed until footage is identified. Preserve originals and keep derived artifacts separate.
- Research/demonstration product only. UI and README must state outputs may be wrong and must not be used alone for safety-critical or enforcement decisions.
- Privacy proposal for owner review: process locally; bind only to localhost; make raw upload retention/deletion explicit; keep JSONL exports local and opt-in; do not include raw frames by default; consider optional face/plate blurring only after requirements are known. This is not legal advice. Owner must specify applicable data-protection requirements and lawful permissions for footage.
- Phase 3 local-footage quality check is blocked until permissioned footage is provided.

## 10. Frontend and design plan

No design references were supplied. In Phases 2–4, build only the unstyled functional Dev Viewer required by the prompt. Before Phase 5, inspect owner references, document a design spec, and obtain approval. Video remains dominant; all statuses, counts and overlays must come from real backend state. No detection/tracking/risk mock data in product UI.

## 11. Proposed first deliverable and exclusions

RodAI v0.1: local video upload and browser-camera input; validated sessions; real detector inference; session-local tracking; frame-aligned boxes/labels/confidence/IDs and movement trails; selection and inspection; genuine live statistics/status/errors; stop safely; export structured results. Exclude trained accident prediction, unsupported physical speeds, claims of safety validation, training UI, cloud deployment, authentication, and database absent approval.

## 12. Phased sequence, effort and acceptance outline

Effort estimates are planning ranges, not commitments; hardware, licensing, footage and owner decisions can change them.

| Phase | Scope and exit evidence | Rough effort |
|---|---|---:|
| 0 | This report, architecture, decisions/questions; owner resolves blockers and approves | 1–2 days |
| 1 | Foundation, pinned environments, local run commands, real health/device status, CI-quality lint/type/test setup | 3–5 days |
| 2 | Validated upload/camera sessions, frame echo pipeline, protocol, export skeleton and plain viewer; frame IDs visibly match | 5–8 days |
| 3 | Real detection, class map, errors, CPU fallback, two model-size benchmarks and local sample quality report | 5–10 days plus footage/hardware access |
| 4 | Session-local tracking/history and viewer; stability/ID-switch limitations documented | 4–7 days |
| 5 | Approved reference-based polished responsive accessible UI and design verification | 5–10 days after references/spec approval |
| 6 | Timestamp-based image-space movement analysis; calibration only with separate approval | 5–10 days |
| 7 | Only justified and documented experimental rules, inspectable evidence/events | 5–10 days after scoped evidence exists |
| 8 | One advanced model per separate approval, with predeclared unseen-video evaluation and real artifacts | Variable; data/training dependent |
| 9 | Dataset/training/simulation laboratory after earlier phases stable and separately approved | Variable; substantial scope |

Each phase plan, deliverables and tests must be reviewed under the master prompt’s approval gates; later phases cannot be started by assuming silence is approval.

## 13. Risks and unmet criteria

- Hardware inventory and inference capability not established.
- Python 3.13 is outside current documented Windows PyTorch Python range.
- Target camera geometry and target environment unknown, so motion/risk design is not ready.
- No sample video, licence, deployment footage or design references.
- Detector code/weight licensing preference unresolved.
- Privacy, retention, export and applicable legal regime unresolved.
- No performance targets can honestly be set until a machine/model/resolution/footage benchmark; propose targets after Phase 3 as the prompt requires.

## 14. Decisions needed

See numbered consolidated questions in `docs/QUESTIONS.md`. Explicitly confirm deployment/footage, camera, privacy, licensing, Python environment, persistence/export, frame transport, concurrency, and design references. Phase 0 is not marked complete until required facts/decisions are resolved sufficiently and the owner explicitly approves the gate.

## 15. Recommended next step

Owner answers the questions and reviews proposals, then sends `APPROVED: Phase 0`. Until then, do not start Phase 1 or create application code.

## Technical references checked on 2026-11-12

- PyTorch [Start Locally](https://docs.pytorch.org/get-started/locally/) currently documents Windows support for Python 3.9–3.12.
- Ultralytics [licensing information](https://docs.ultralytics.com/) describes AGPL-3.0 and a separate Enterprise licence.
- The original [RT-DETR repository](https://github.com/lyuwenyu/RT-DETR) identifies its repository code as Apache-2.0; this does not establish the licence of every checkpoint or dataset.
- Railway [plans and pricing](https://docs.railway.com/pricing/plans) currently list (among others) Trial at 1 GB RAM/2 vCPU/0.5 GB volume, Free at 0.5 GB RAM/1 vCPU/0.5 GB volume, and Hobby at 5 GB volume, with metered CPU/RAM/storage/egress usage and monthly subscription/usage credits. These are mutable platform details, not a committed estimate for RodAI.
- Railway [volume limits](https://docs.railway.com/volumes/reference) document plan-dependent volume sizes and note that a service can have one volume, replicas cannot be used with volumes, and deployments cannot concurrently mount the same service volume. This affects app architecture, upgrade downtime, persistence and future scaling.
- Railway [networking limits](https://docs.railway.com/networking/public-networking/specs-and-limits) document WebSockets over HTTP/1.1 and that WebSocket connections are exempt from normal request-duration/inactivity limits. HTTP request bodies still have a five-minute upload completion limit; long video uploads therefore need bounded sizes and/or chunked transfer.
- Railway [service storage docs](https://docs.railway.com/services) explain that deployment filesystem outside a mounted volume is ephemeral. Persistent video, exports, and downloaded weights must stay on the volume.

## Consolidated owner decisions and architecture reconciliation — 2026-11-14

The owner supplied a consolidated Phase 0 decision document. These decisions are recorded in `docs/DECISIONS.md`; they are requirements for planning and **do not approve Phase 0**. The owner explicitly said to complete the report and wait for `APPROVED: Phase 0` before starting Phase 1. Phase 1 and Phase 2 code were already implemented/pushed before this latest instruction; this is historical context, not a reason to infer approval for any next phase.

### Confirmed target and architecture

- Selected-user research and demonstration, initially targeting Rwanda/Kigali; do not hardcode geography. Support fixed roadside/CCTV, dashcam, uploads and browser camera, with extensible source adapters.
- Local-first inference, Docker/Compose packaging, PostgreSQL as primary application store, Railway target for an eventual controlled hosted service, same-origin app serving built frontend and API, persistent Railway volume, CPU-only hosted inference.
- Invite-only owner-managed hosted accounts, no self-registration, secure password hashing/cookies. Public live camera is out of the first hosted release; local camera remains in scope.
- Initial upload limits: 500 MB, 600 seconds, one concurrent processing session. PostgreSQL stores searchable application/session metadata; portable JSONL exports do not replace it.
- Offline video frames are ordered. Browser camera uses binary JPEG over `rodai.v1`, frame IDs and capture timestamps, bounded newest-frame-wins, counted drops, configurable size/quality, proposed capture ceiling 1280x720.
- V0.1 prioritizes actual detection, tracking and visualization; annotated video is optional and accident prediction is not part of the promised first demo.

### Privacy, licensing and operations

- Privacy defaults: private by default, uploaded video up to 7 days, session metadata/results 30 days, exports 7 days, configurable deletion; no source frames in exports by default. Face/plate blur is needed before external sharing, and anonymization cannot be claimed without checking the result. Rwanda personal-data requirements need qualified interpretation for the selected use.
- Commercial compatibility is required. Prefer permissive software; do not use AGPL-3.0 without explicit approval. Review source, model weights and data separately. No detector or weight is selected.
- Use isolated Python 3.12 and leave host Python 3.13.2 untouched. Require CPU fallback; optional GPU waits on hardware inspection.
- Planned hostname is `rodai.cursorclick.dev`; the Railway-provided domain is fallback. Do not configure DNS or purchase anything without approval. Railway plan/spend limit is not decided; no paid provisioning or deployment is authorized.

### Current mismatch and phase boundary

The current source implements one-session limits and the existing 500 MB/600-second settings. It currently deletes original uploads after processing and leaves results until the user deletes the session; automated 7-day/30-day/7-day retention is not implemented. Browser capture currently uses source resolution and fixed JPEG quality 0.82, with no 1280x720 cap or configurable quality. These are explicit implementation gaps to resolve in an approved plan. Authentication, public deployment, detector, tracking and risk analysis are also absent.

Current Compose names are preserved: service/container `rodai-db`; configured database name `rodai`; user `rodai`. Do not rename or alter connection settings based on the textual shorthand in the owner questionnaire.

### Phase 0 exit status

Architecture and owner decisions are documented; remaining questions are listed in `docs/QUESTIONS.md`. Hardware, representative permissioned samples, privacy-law application and Railway spend limit remain open facts/decisions. Phase 0 is **not approved and not marked complete**. Stop here and wait for the owner to review and send `APPROVED: Phase 0`.

## Phase 0 closeout response — 2026-11-14

The owner's latest response confirms the previously recorded decisions and adds the following refinements:

- Railway hostname planning is `rodai.cursorclick.dev`; DNS provider is Cloudflare. Do not change DNS or purchase a domain without separate approval. Local Compose is the priority; no paid Railway provisioning/deploy before an explicit plan and monthly cap are approved.
- Hardware confirmed so far: Windows machine, Intel processor, 32 GB RAM. Exact Windows edition/build, processor model, GPU/VRAM, CUDA/driver and free disk remain unverified. Keep CPU support mandatory; do not install GPU tooling or change drivers without approval.
- No owner-provided sample collection is ready. Never use random or merely public footage as if licensed. Document provenance and usage rights before accepting a sample. Synthetic fixtures remain appropriate for deterministic pipeline mechanics, but they cannot satisfy representative footage quality acceptance.
- Technical retention defaults are accepted (video 7 days, results/session history 30 days, stored exports 7 days, models/checkpoints until manually removed); these do not establish legal compliance. Rwanda privacy-law questions are listed in `docs/QUESTIONS.md`. Keep content private, make deletion auditable, and consider face/plate blur before external sharing.
- Phase 2 must be brought into conformance before Phase 3: automatic expiry/deletion, configurable camera capture, one-session conflict behavior and live drop accounting. Test cases and measurable exit criteria follow below.

### Candidate external smoke-test clip (not yet downloaded or accepted as target footage)

Wikimedia Commons lists **“Bangalore 20220814 155101.webm”** by L. Shyamal as the creator's own work and dedicated under CC0 1.0. File-page metadata reports 2:07 duration, 1920x1080, 425.86 MB, WebM/VP9. The page offers a 720p transcode. It fits current upload size/duration and `.webm` format. It can be considered for local ingestion smoke testing after inspection for identifiable people/plates; do not put it in Git or use it as a Kigali quality sample. Candidate/source and licence: https://commons.wikimedia.org/wiki/File:Bangalore_20220814_155101.webm. No download has been made.

### Railway cost estimate (planning only; USD, checked against Railway official pricing on 2026-11-14)

Railway's current Hobby plan is $5/month and includes $5 of resource usage. The official listed container rates are $10 per GB-month RAM, $20 per vCPU-month, $0.15 per GB-month volume storage, and $0.05 per GB egress. Hobby currently lists a 5 GB volume limit. Railway bills for a running service's CPU/RAM even without traffic. This estimate excludes tax, exchange fees, model hosting/inference load and exceptional traffic.

| Illustrative continuously-running local-demo deployment | RAM average (app + PostgreSQL) | CPU average (combined) | Volume | Monthly egress | Estimated resource usage / total Hobby bill |
|---|---:|---:|---:|---:|---:|
| Lower-use scenario | 0.5 GB | 0.05 vCPU | 5 GB | 10 GB | $7.25 |
| Higher baseline scenario | 1.0 GB | 0.10 vCPU | 5 GB | 10 GB | $13.25 |

Calculation example for higher baseline: RAM $10 + CPU $2 + volume $0.75 + egress $0.50 = $13.25 resource usage; the $5 Hobby subscription credit offsets the first $5, so estimated total is $13.25, not $18.25. These average resource sizes are unmeasured assumptions, not a quote. Detection CPU usage may be materially higher and must be measured locally; therefore keep inference local for now. At the 500 MB upload cap, a 5 GB volume holds at most 10 maximum-size originals before accounting for database/results/model files, so quotas and 7-day expiry are necessary. No plan is recommended or approved yet.

Official pricing references: [Railway plan and resource rates](https://docs.railway.com/pricing/plans), [how Railway bills active services](https://docs.railway.com/pricing/understanding-your-bill).

### Phase 2 conformance plan and acceptance criteria (before Phase 3)

These items are planning requirements only. They must be implemented and verified in an approved phase; no present feature claim should imply they are already done.

**Automatic retention and deletion**

- Store policy and expiry timestamps for original uploads (7 days), session results/metadata (30 days), and server-held export artifacts (7 days); make retention values configurable through validated settings.
- Run a scheduled expiry sweep at least hourly. An expired artifact is deleted within 60 minutes of its expiry under normal operation. The sweep records artifact type, internal ID, expiry, attempt time and outcome without logging frame content or secrets.
- Remove the file first and delete its associated database records only after successful filesystem deletion. On failure, preserve/reconcile the record, log a structured failure, surface a real operational status, and retry on the next sweep. Missing files and orphan files are reported and handled idempotently.
- Never remove a model/checkpoint referenced by an experiment or model-registry record; model artifacts remain until explicitly deleted after references are cleared.
- Tests with a controllable clock cover not-yet-expired and just-expired records, each artifact class, linked-record deletion, retry after injected filesystem failure, orphan/missing files, idempotent repeated sweeps, and protection of referenced model files. Acceptance: all eligible expired records are handled; no unexpired or referenced model artifact is deleted; injected failures remain observable and retryable; audit outcome exists for every attempt.
- A file downloaded by a user is outside RodAI's control and cannot be remotely deleted; explain that distinction in the export UX.

**Configurable browser-camera capture**

- Default maximum frame size is 1280x720. Preserve aspect ratio and downscale larger camera input; offer lower resolutions. Make JPEG quality configurable; proposed validated range is 0.50–0.95 with current 0.82 as default. Reject invalid/unsupported settings at session creation.
- Frontend sends selected settings when creating a live session. Backend validates them and returns the effective settings in the session-start message; frontend uses those effective settings. Include effective dimensions and quality in session/frame metadata.
- Tests cover default values, supported lower-resolution choices, invalid dimensions/quality, downscaling, settings negotiation, and exact frame/session metadata consistency. Acceptance: no transmitted frame exceeds 1280x720 by default; effective dimensions remain within the user-selected maximum; requested and acknowledged quality match; invalid settings receive a clear 4xx response.
- Any setting above 1280x720 remains disabled until benchmarked on actual development hardware and approved. Record sustained FPS, per-frame latency, CPU/RAM and dropped-frame rate for the chosen resolution/quality before expanding caps.

**Session cap and frame accounting**

- Keep `RODAI_MAX_CONCURRENT_SESSIONS=1`. Tests attempt a second video while one is active and a camera while one is active; both receive HTTP 409 with a clear message. Verify a stopped/completed/failed session releases the slot and repeated starts cannot replace active work.
- Live frames carry monotonically increasing IDs and `dropped_since_last`. Tests verify accepted frames preserve IDs/timestamps, dropped counts are reported exactly once and accumulated totals match; malformed or out-of-order frames are rejected. Offline video must process ordered frames without silently dropping any.
- Acceptance: never more than one active session; every competing request receives an explicit conflict; live dropped-frame totals are visible in session detail/export; offline processed count equals decoded count unless a clearly reported error/stop terminates processing.

### Sample-video metadata and acceptance policy

For every candidate, record at minimum: source URL/creator; retrieval date/checksum; copyright licence and specific allowed use; permission/restrictions; recording location and camera/source type; context; duration; resolution; FPS; whether people/plates are identifiable; storage/retention; and whether the sample is for pipeline smoke, detector evaluation or target-region acceptance. The Bangalore CC0 file above is an optional pipeline smoke candidate only. Synthetic fixtures test deterministic mechanics. Representative detector-quality acceptance for the target remains blocked until permissioned Kigali/Rwanda footage is supplied and inspected.

## Addendum impact and revised implementation plan (original note)

The addendum supersedes conflicting master-prompt rules. The approved target is now local-first inference with Docker packaging, Railway deployment, PostgreSQL persistence, CPU-only production inference, environment-variable configuration, and authentication for public access. Phase 1 now needs Dockerfiles, Compose, `.env.example`, Pydantic Settings, PostgreSQL/Alembic, and container tests. Phase 1B is a distinct Railway deployment gate. Every later phase must include Docker/Compose acceptance; deployment checks and Railway CPU measurements are added at the specified gates.

The single app service serving frontend assets and API is the recommended default. PostgreSQL in Compose is recommended for local/prod parity; SQLite remains an owner-selectable local simplification with acknowledged drift. A Railway volume is required for persisted uploads/results/weights. Since attached volumes currently disallow replicas and replacement deployments cannot overlap mount access, start with one app replica and one Uvicorn worker, and plan deploy interruption and backups. Use resumable/chunked upload or strict upload limits because the Railway edge has a five-minute request-body completion limit. The WebSocket path is suitable for live frames, but bandwidth and end-to-end latency still need measured budgets.

The following are not yet known and cannot be assumed: Railway subscription and spend limit, domain/DNS, user audience, retention/privacy rules, upload caps, whether camera is needed on public deployment, detector licensing, and local Postgres-vs-SQLite preference. See questions 12–19 in `docs/QUESTIONS.md`. Do not deploy a publicly reachable service before authentication and detector licensing are resolved.

Phase sequence is now: Phase 0 revised design/owner choices → Phase 1 containerized local foundation → Phase 1B Railway skeleton/auth/health/volume/rollback → Phase 2 video/session protocol → subsequent phases with addendum container and deployment evidence. Each remains subject to the prompt’s phase approval gate.
