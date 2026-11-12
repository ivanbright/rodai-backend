# RodAI

RodAI is a local-first road perception and movement analysis laboratory. Its outputs are experimental, may be wrong, and must not be used as the sole basis for safety-critical or enforcement decisions. Accident prediction is not implemented.

## Current status

Phase 1 foundation only. The app reports actual API, PostgreSQL, device configuration and mounted data-volume status. Video ingestion, detection, tracking and model inference are unavailable until later approved phases.

## Requirements

- Docker Desktop with Linux containers and Docker Compose v2.
- A supported Python 3.12 runtime for backend development outside containers.
- Node.js 22 LTS for frontend development outside containers.
- Enough disk for Docker images, PostgreSQL data and later model weights. Hardware and minimum capacity have not yet been benchmarked.

## Run locally

1. Copy `.env.example` to `.env` and adjust local settings if needed. Never use the example secret for a shared deployment.
2. Run `docker compose up --build` from the repository root.
3. Open `http://localhost:5173` for the Vite development viewer or `http://localhost:8000/api/v1/health` for backend health.
4. Apply database migrations explicitly with `docker compose run --rm backend alembic upgrade head`.

Local containers use PostgreSQL to match the deployment engine. The Vite server proxies `/api` to FastAPI. The backend serves the production frontend build from the same origin.

## Tests and quality checks

Run `scripts/run-tests.ps1` from PowerShell. Backend tests use pytest; frontend tests use Vitest. Run backend lint with `docker compose run --rm backend ruff check .` and the frontend lint script with `docker compose run --rm frontend npm run lint`.

The present workspace environment has no running Docker daemon, so Compose commands have not yet been verified here.

## Configuration and deployment

See [Docker and Compose](docs/docker.md), [deployment](docs/deployment.md), [security](docs/security.md), [privacy](docs/privacy.md), and [licences](docs/licences.md). Railway deployment is a separate Phase 1B gate; do not expose this foundation build publicly before authentication, privacy, licensing, quotas and secrets are configured.
