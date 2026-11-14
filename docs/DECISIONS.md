# RodAI Decision Log

Updated 2026-11-14. The owner subsequently stated “I approved everything” and directed the next phases to begin. This is recorded as explicit Phase 0 approval and authorization to continue implementation. Approval does not change the constraints and limits recorded below.

| ID | Owner decision / requirement | Status or remaining condition |
|---|---|---|
| P0-1 | Initial demonstration is for selected users in Rwanda, with Kigali footage important; architecture must support other locations. | Target accepted; permissioned target-region footage not yet provided. |
| P0-2 | Support roadside/CCTV, dashcam, uploaded video and browser cameras; future sources can include drone/phone. Record source, licence/permission, location/context, duration, resolution, FPS, restrictions and identifiable-person/plate presence. | Requirement accepted; sample/source manifest to be added. No approved local sample collection supplied. |
| P0-3 | Privacy defaults: private data; uploaded originals retained at most 7 days; session metadata/results 30 days; exported files 7 days; configurable; users can delete uploads/results. No original frames in exports by default. Blur faces/plates before external sharing; do not claim anonymization without checking. | Technical defaults accepted, not legal compliance. Automatic retention/deletion and auditable failure handling are not implemented. |
| P0-4 | Keep future commercial distribution possible; prefer permissive code; no AGPL-3.0 without explicit approval. Review source code, weights and datasets separately. | Requirement accepted; detector and weights remain unselected. |
| P0-5 | Require CPU inference; GPU optional only after verification. Use isolated Python 3.12 and leave installed Python 3.13.2 untouched. | Requirement accepted; exact Windows/CPU/GPU/VRAM/CUDA details remain unknown. |
| P0-6 | PostgreSQL is primary persistent storage; JSONL is for portable exports/logs, not a replacement for the database. Preserve current Compose settings. | Compose service/container is `rodai-db`; actual configured database name and user are `rodai`. |
| P0-7 | Annotated video export is not mandatory in v0.1; prioritize detection, tracking and visualization. | Accepted. |
| P0-8 | Use binary JPEG WebSocket frames with client IDs/timestamps; uploaded video is ordered; live preview is bounded newest-frame-wins with counted drops. Configure resolution/quality, start with max 1280x720, lower when needed. | Design accepted; current implementation needs explicit cap/config verification. |
| P0-9 | One simultaneous processing session for v0.1; reject a second clearly, do not replace or create an unbounded queue. | Accepted; enforcement needs verification. |
| P0-10 | UI direction: minimal professional blue/white, responsive and purposeful. Owner will provide design references before Phase 5; avoid generic glassmorphism. | Accepted; Phase 5 awaits references. |
| DEP-1 | Railway is the target; frontend and API run as separate services, with PostgreSQL and a persistent API volume. Production inference is CPU-only; training/heavy experimentation remains local/off-platform. | Owner selected split frontend/API deployment to remove frontend build dependency from API; no Railway deployment performed. |
| DEP-2 | Invite-only, owner-managed accounts; self-registration disabled; secure password hashing and session cookies; no hardcoded secrets. Public browser-camera streaming is not required for first hosted release. | Accepted requirement; auth/deployment implementation pending. |
| DEP-3 | Plan around `rodai.cursorclick.dev`; DNS managed through Cloudflare. Railway-provided hostname is temporary fallback. Do not purchase a domain or change DNS without separate approval. | Domain/DNS details corrected; DNS/deployment not configured. |
| DEP-4 | Prioritize local Docker Compose. Prepare a cost estimate before asking for Railway plan/spend approval. No paid provisioning/deployment until a specific plan and monthly ceiling are approved. | Estimate added to Phase 0 handover; spending approval still open. |
| DEP-5 | Start with current limits: 500 MB upload, 600-second video, one session. Retain uploaded videos 7 days, results/history 30 days, server-held exports 7 days; retain models/checkpoints until manually deleted. Make policies configurable and deletion explicit. | Technical defaults accepted; expiry scheduler and deletion audit behavior not implemented. Downloads already saved by users cannot be revoked by RodAI; explain this in UX. |
| DEP-6 | PostgreSQL in local Compose; inspect current config before changes. | Current service name `rodai-db`, database `rodai`, user `rodai`; preserve as configured. |

## Still open

- Phase 0 gate: approved by the owner's explicit follow-up on 2026-11-14.
- Permissioned sample footage/source manifests; exact hardware inventory; Windows edition and CPU/GPU details.
- Applicable privacy-law interpretation and any required legal review for intended footage/use.
- Railway plan and spend ceiling before provisioning or deployment.
- Exact detector implementation, weights, licences, class map and evaluation plan.
- Phase 2 conformity is implemented in the current working tree: retention, camera limits/settings, concurrency and drop reporting have deterministic tests; apply Alembic revision `0002_retention` to an existing database before running the updated API.
- Authentication/deployment remains future work; public deployment is not part of this local demo.

## Phase 2 completion requirements before Phase 3

These were requirements and are now implemented in the current working tree. The latest acceptance evidence and remaining limitations are in `docs/handovers/phase-0.md` and `docs/handovers/phase-3.md`.

- Expire server-held uploaded videos after 7 days, results/history after 30 days, and stored export artifacts after 7 days; keep policy configurable, log deletions, safely retry failures, and protect model/checkpoint files referenced by experiments.
- Browser capture defaults to max 1280x720, supports lower sizes, configurable JPEG quality, server-side validation and negotiated/effective settings; higher settings require measured performance evidence.
- Enforce the one-active-session cap for video and camera, reject another with clear conflict, and account for dropped live frames end-to-end.
- Add deterministic tests using synthetic video and a controllable clock. Representative target-region evaluation still requires footage with verified source/permission and metadata.
