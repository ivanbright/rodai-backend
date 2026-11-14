# RodAI Assumptions and constraints

Updated 2026-11-14. Owner-provided decisions in `DECISIONS.md` replace earlier provisional assumptions.

## Confirmed requirements

- Initial target is selected-user research/demonstration in Rwanda, including Kigali traffic, without hardcoding the system to that location.
- CPU inference is mandatory; GPU acceleration is optional after the hardware is identified.
- PostgreSQL is the primary persistent store, and the existing Compose PostgreSQL configuration must be preserved.
- One processing session, 500 MB uploads, 600-second duration, binary WebSocket JPEG camera frames with frame IDs/timestamps, ordered upload processing, bounded live processing with drop counts.
- Commercial compatibility is desired; no AGPL-3.0 without explicit approval; code, weights and datasets each require a licence review.
- Privacy/retention defaults, invite-only hosted access, same-origin Railway topology and the planned domain are recorded in `DECISIONS.md`.

## Unknown facts and implementation gaps (not assumptions)

- Host GPU/VRAM/CUDA, exact Windows and CPU details remain unverified; current Docker PyTorch is CPU-only.
- No permissioned Rwanda/Kigali sample footage has been supplied. Do not fetch or store unreviewed footage.
- Retention timers for 7-day uploads/exports and 30-day results are not implemented. Current upload originals are temporary during processing and removed afterward; result/session artifacts remain until explicitly deleted.
- Camera resolution cap/configuration and JPEG quality configuration are not implemented; current frontend captures at source resolution with fixed JPEG quality 0.82.
- Detector, tracking, movement analysis and risk analysis are not implemented.
- Railway budget is unset, and no Railway deployment or paid service is authorized. `rodai.cursorclick.dev` is planning information only; no DNS changes are authorized.
- Phase 0 approval has not been given. Do not start another implementation phase until the owner reviews the report and sends `APPROVED: Phase 0`.
