# Docker and Compose

## Local services

- `backend`: FastAPI, PostgreSQL client, CPU-only PyTorch and built frontend assets. One Uvicorn worker is configured because session state and model memory are process-local.
- `frontend`: Node 22 Vite dev server with hot reload.
- `postgres`: PostgreSQL 17 for local/production engine parity.

`docker compose up --build` starts the services. Apply migrations as an explicit operation with `docker compose run --rm backend alembic upgrade head`; app startup does not run migrations. Run tests with `scripts/run-tests.ps1`.

## Image details

Backend uses a multi-stage build with `python:3.12.8-slim-bookworm`; the frontend build stage uses `node:22.13.1-alpine3.21`. Production installs CPU-only PyTorch 2.14.1/torchvision 0.29.1 and `opencv-python-headless`, runs as a non-root user, writes app data to `/var/lib/rodai`, and logs to stdout/stderr. Model weights are not included.

These image tags are exact version tags, not digest-pinned. Image digests and final image sizes are not recorded because the Docker daemon is unavailable in the current environment; record both after a successful clean build before Phase 1 acceptance.

## Volumes and commands

Compose persists PostgreSQL data and RodAI data in separate named volumes. Video/export/model artifacts belong in the RodAI volume, never the container layer or PostgreSQL. Do not put datasets, checkpoints or secrets in the build context.

- Start backend + PostgreSQL: `scripts/run-backend.ps1`
- Start viewer + backend + PostgreSQL: `scripts/run-frontend.ps1`
- Tests: `scripts/run-tests.ps1`

These scripts require Docker Desktop's Linux-container daemon to be running.
