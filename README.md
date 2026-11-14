# RodAI

RodAI is a local-first road perception and simulation laboratory. Its outputs are experimental and must not be used as the sole basis for safety-critical or enforcement decisions. It does not provide validated accident prediction or real-world crash prevention.

## Current status

The local demo has two workspaces: a **Simulation lab** with three repeatable scripted road-conflict scenes, a rule-based risk countdown, and a simulated braking response; and **Video analysis**, which runs a pinned CPU DETR object detector on uploaded video. The simulation is synthetic ground-truth logic, not a trained model or evaluation of camera perception. The video detector identifies common road-user objects; it does not track them or predict accidents.

See [Phase 4](docs/handovers/phase-4.md) for the simulation-library direction and current limits, and [Phase 3](docs/handovers/phase-3.md) for detector evidence.

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
