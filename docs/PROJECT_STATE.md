# RodAI Project State

Updated: 2026-11-14

- **Phase 2:** Retention and camera-configuration requirements implemented, tested and applied to the local Compose database.
- **Phase 3:** First CPU detector integrated. A 14-frame road-video smoke upload completed with detections on every frame. Representative Rwanda/Kigali validation and performance acceptance remain pending.
- **Phase 4:** The first interactive simulation-lab slice is implemented. Three scripted scenarios show agent motion, a deterministic time-to-conflict/risk indicator, and an optional simulated braking outcome. It is not a trained predictive model and does not evaluate camera perception. The richer test library, ground-truth recording and evaluation metrics remain to be built.
- **Local runtime:** PostgreSQL and API are healthy; CPU selected; DETR model and retention report available. Frontend is at port 5173; API at 8001 because another local service occupies host port 8000. Start with `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build`.
- **Verification:** Frontend production build passed after the lab addition. Backend previously passed 13 tests/Ruff; frontend previously passed build, lint and 2 Vitest tests before this slice.
- **Outstanding:** scenario-library generation and evaluation, tracking, video export experience, hardware inventory and measured performance, permissioned representative footage, privacy review and plate blurring before sharing, and design references before Phase 5.

See `docs/handovers/phase-3.md`, `docs/handovers/phase-4.md`, `docs/DECISIONS.md`, and `docs/QUESTIONS.md`. Planned functionality is not counted as implemented.
