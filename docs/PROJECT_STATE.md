# RodAI Project State

Updated: 2026-11-14

- **Phase 2:** Retention and camera-configuration requirements implemented, tested and applied to the local Compose database.
- **Phase 3:** First CPU detector integrated. A 14-frame road-video smoke upload completed with detections on every frame. Representative Rwanda/Kigali validation and performance acceptance remain pending.
- **Phase 4:** A small scripted SVG simulation demonstration exists, but it is not the intended real-video road-safety lab and is not validation evidence. Its deterministic risk score is unrelated to detector output. Product direction and measurable stages are documented in `docs/PRODUCT_VISION.md`.
- **Phase 5:** Prototype online road-user tracking is implemented for uploaded and browser-camera sessions. Track IDs, image-plane trails and pixel-per-second motion values are included in results and rendered over video. Identity stability and tracking accuracy have not been benchmarked on labeled footage.
- **Local runtime:** PostgreSQL and API are healthy; CPU selected; DETR model and retention report available. Frontend is at port 5173; API at 8001 because another local service occupies host port 8000. Start with `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build`.
- **Verification:** Frontend production build passed after the lab addition. Backend previously passed 13 tests/Ruff; frontend previously passed build, lint and 2 Vitest tests before this slice.
- **Outstanding:** tracking evaluation on labeled real footage, calibrated movement/speed measures, CCTV/RTSP ingestion, event/conflict logic evaluated on labeled footage, operator alert review, hardware inventory and performance benchmarks, permissioned representative footage, privacy review and plate blurring before sharing. The scripted simulation is not a substitute for these requirements.

See `docs/handovers/phase-3.md`, `docs/handovers/phase-4.md`, `docs/handovers/phase-5.md`, `docs/PRODUCT_VISION.md`, `docs/DECISIONS.md`, and `docs/QUESTIONS.md`. Planned functionality is not counted as implemented.
