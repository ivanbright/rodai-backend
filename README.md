# RodAI

RodAI is being built to analyze real road-camera video and provide road-safety information for human review. The current prototype detects a limited set of road-user objects and applies short-term image-plane tracking to uploaded video. It does not yet ingest CCTV streams, estimate calibrated physical speeds, detect or predict accidents, or prevent crashes. Outputs are experimental and must not be used as the sole basis for safety-critical or enforcement decisions.

## Current status

The local demo opens into **Video analysis**, which runs the pinned CPU DETR detector and prototype tracker on uploaded video. The analysis appears over the video in the page; export to WebM is optional. The JSONL frame log is available under technical details for developers. The former scripted SVG simulation tab has been removed. An experimental image-plane trajectory heuristic can highlight pairs whose current tracks may converge within three seconds; this is not a validated collision prediction or safety feature. See the [product roadmap](docs/PRODUCT_VISION.md), [Phase 5 tracking limits](docs/handovers/phase-5.md), and [Phase 6 user workflow](docs/handovers/phase-6.md).

See [Product Vision](docs/PRODUCT_VISION.md) for the intended real-video product, build sequence and measurable acceptance evidence. See [Phase 3](docs/handovers/phase-3.md) for detector evidence and [Phase 4](docs/handovers/phase-4.md) for the scripted demonstration's limits.

## Requirements

- Docker Desktop with Linux containers and Docker Compose v2.
- A supported Python 3.12 runtime for backend development outside containers.
- Node.js 22 LTS for frontend development outside containers.
- Enough disk for Docker images, PostgreSQL data and model weights. Hardware performance remains unbenchmarked.

## Run locally

From the repository root, start the local stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d rodai-db
docker compose -f docker-compose.yml -f docker-compose.local.yml run --build --rm rodai-api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Open `http://localhost:5173` to process a local MP4, MOV, MKV, WebM or AVI. The latest saved video session reopens in the page with its annotated playback. The default is 2 analyzed frames per second; higher rates take longer on CPU and sparse sampling can miss fast events. Wait for the first analyzed frame before stopping. Export an annotated WebM only if you need a shareable file; the JSONL link is in **Technical data for developers**. The Compose override publishes the API on port 8001 because the default API host port may be occupied by another local service. API health is at `http://localhost:8001/api/v1/health`.

The first video-analysis inference downloads and caches pinned model weights into the persistent `rodai_data` volume.

The local **Benchmark library** lists official traffic datasets and can analyze clips that you have permission to use after you place them under the ignored `datasets/` folder and register them in [`datasets/catalog.json`](datasets/catalog.json). It streams the local source file read-only; no sample benchmark video is included or automatically downloaded. See [`datasets/README.md`](datasets/README.md) for the clip metadata format and terms-review gate. The library cannot be enabled in staging or production.

Local Compose uses PostgreSQL and the Vite development proxy. In Railway, deploy the frontend and API as separate services; set the frontend's `VITE_API_BASE_URL` to the public API origin and allow the frontend origin in `RODAI_ALLOWED_ORIGINS`.

## Quality checks

Run `scripts/run-tests.ps1` from PowerShell. Backend tests use pytest; frontend tests use Vitest. Backend lint can be run with `docker compose run --rm rodai-api ruff check .`; frontend lint with `docker compose run --rm rodai-frontend npm run lint`. Software tests do not validate real-world perception or warning accuracy.

## Configuration and deployment

See `docs/docker.md`, `docs/deployment.md`, `docs/security.md`, `docs/privacy.md`, and `docs/licences.md`. Railway deployment is a separate approval gate; do not expose the service publicly before authentication, privacy, licensing, quotas and secrets are resolved.
