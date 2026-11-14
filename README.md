# RodAI

RodAI is being built to analyze real road-camera video and provide road-safety information for human review. The current prototype detects a limited set of road-user objects in uploaded video. It does not yet track road users, estimate calibrated physical speeds, ingest CCTV streams, detect or predict accidents, or prevent crashes. Outputs are experimental and must not be used as the sole basis for safety-critical or enforcement decisions.

## Current status

The local demo includes **Video analysis**, which runs the pinned CPU DETR object detector on uploaded video. It can display detections alongside playback and return frame-level results. A separate scripted SVG simulation workspace is also present as a limited software demonstration; it is not real road footage, a validated model, or progress evidence for CCTV incident detection. See [the product vision and acceptance roadmap](docs/PRODUCT_VISION.md) and [Phase 3 evidence and limits](docs/handovers/phase-3.md).

See [Product Vision](docs/PRODUCT_VISION.md) for the intended real-video product, build sequence and measurable acceptance evidence. See [Phase 3](docs/handovers/phase-3.md) for detector evidence and [Phase 4](docs/handovers/phase-4.md) for the scripted demonstration's limits.

## Requirements

- Docker Desktop with Linux containers and Docker Compose v2.
- A supported Python 3.12 runtime for backend development outside containers.
- Node.js 22 LTS for frontend development outside containers.
- Enough disk for Docker images, PostgreSQL data and model weights. Hardware performance remains unbenchmarked.

## Run locally

From the repository root, start the local stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Open `http://localhost:5173`. Choose **Simulation lab** to run controlled scenarios, or **Video analysis** to process a local MP4, MOV, MKV, WebM or AVI. The Compose override publishes the API on port 8001 because the default API host port may be occupied by another local service. API health is at `http://localhost:8001/api/v1/health`.

The first video-analysis inference downloads and caches pinned model weights into the persistent `rodai_data` volume. Synthetic lab scenarios do not require an internet download or model weights.

Local Compose uses PostgreSQL. The frontend proxies `/api` to FastAPI; the production API image also serves the built frontend.

## Quality checks

Run `scripts/run-tests.ps1` from PowerShell. Backend tests use pytest; frontend tests use Vitest. Backend lint can be run with `docker compose run --rm rodai-api ruff check .`; frontend lint with `docker compose run --rm rodai-frontend npm run lint`. Synthetic scenario outcomes do not validate real-world perception accuracy.

## Configuration and deployment

See `docs/docker.md`, `docs/deployment.md`, `docs/security.md`, `docs/privacy.md`, and `docs/licences.md`. Railway deployment is a separate approval gate; do not expose the service publicly before authentication, privacy, licensing, quotas and secrets are resolved.
