# RodAI Decision Log

Updated 2026-11-14. Decisions below are owner-provided requirements from the consolidated Phase 0 response. They guide the architecture but do **not** constitute Phase 0 approval. No new implementation phase is authorized until `APPROVED: Phase 0` is received.

| ID | Owner decision / requirement | Status or remaining condition |
|---|---|---|
| P0-1 | Initial demonstration is for selected users in Rwanda, with Kigali footage important; architecture must support other locations. | Target accepted; no permissioned sample video yet. |
| P0-2 | Support roadside/CCTV, dashcam, uploaded video and browser cameras; future sources can include drone/phone. Record source, licence/permission, location/context, duration, resolution, FPS, restrictions and identifiable-person/plate presence. | Requirement accepted; sample/source manifest not implemented. |
| P0-3 | Privacy defaults: private data; uploaded originals retained at most 7 days; session metadata/results 30 days; exported files 7 days; configurable; users can delete uploads/results. No original frames in exports by default. Blur faces/plates before external sharing; do not claim anonymization without checking. | Requirement accepted; retention jobs and configurable policies are not implemented. Rwanda legal obligations require qualified review. |
| P0-4 | Keep future commercial distribution possible; prefer permissive code; no AGPL-3.0 without explicit approval. Review source code, weights and datasets separately. | Requirement accepted; detector and weights remain unselected. |
| P0-5 | Require CPU inference; GPU optional only after verification. Use isolated Python 3.12 and leave installed Python 3.13.2 untouched. | Requirement accepted; exact Windows/CPU/GPU/VRAM/CUDA details remain unknown. |
| P0-6 | PostgreSQL is primary persistent storage; JSONL is for portable exports/logs, not a replacement for the database. Preserve current Compose settings. | Compose service/container is `rodai-db`; actual configured database name and user are `rodai`. |
| P0-7 | Annotated video export is not mandatory in v0.1; prioritize detection, tracking and visualization. | Accepted. |
| P0-8 | Use binary JPEG WebSocket frames with client IDs/timestamps; uploaded video is ordered; live preview is bounded newest-frame-wins with counted drops. Configure resolution/quality, start with max 1280x720, lower when needed. | Design accepted; current implementation needs explicit cap/config verification. |
| P0-9 | One simultaneous processing session for v0.1; reject a second clearly, do not replace or create an unbounded queue. | Accepted; enforcement needs verification. |
| P0-10 | UI direction: minimal professional blue/white, responsive and purposeful. Owner will provide design references before Phase 5; avoid generic glassmorphism. | Accepted; Phase 5 awaits references. |
| DEP-1 | Railway is the target; container-based single app serves backend and built frontend from the same origin. PostgreSQL and a persistent volume are required. Production inference is CPU-only; training/heavy experimentation remains local/off-platform. | Accepted architecture; no Railway deployment performed. |
| DEP-2 | Invite-only, owner-managed accounts; self-registration disabled; secure password hashing and session cookies; no hardcoded secrets. Public browser-camera streaming is not required for first hosted release. | Accepted requirement; auth/deployment implementation pending. |
| DEP-3 | Plan around `rodai.cursorclick.dev`; Railway-provided hostname is temporary fallback. Do not buy/configure domain or DNS without owner approval. | Domain choice for planning only; DNS/deployment not configured. |
| DEP-4 | Lowest practical Railway cost, but no monthly ceiling/plan is approved. Do not provision paid resources or deploy services that can incur unexpected costs without approval. | Spending limit is an open blocker for deployment. |
| DEP-5 | Start with current limits: 500 MB upload, 600-second video, one session. Retain videos 7 days, results/history 30 days, exports 7 days; retain model files until manually deleted. Make policies configurable and deletion explicit. | Limits mostly match current config; automatic retention is not implemented. |
| DEP-6 | PostgreSQL in local Compose; inspect current config before changes. | Current service name `rodai-db`, database `rodai`, user `rodai`; preserve as configured. |

## Still open

- Phase 0 gate: owner explicitly withheld approval pending review of the architecture report.
- Permissioned sample footage/source manifests; exact hardware inventory; Windows edition and CPU/GPU details.
- Applicable privacy-law interpretation and any required legal review for intended footage/use.
- Railway plan and spend ceiling before provisioning or deployment.
- Exact detector implementation, weights, licences, class map and evaluation plan.
- Phase 2 implementation conformity: concurrency enforcement and configurable camera resolution/JPEG quality need review against the newly confirmed decisions.
- Retention behavior and authentication are future implementation requirements, not current features.
