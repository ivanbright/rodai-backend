# Docker and Compose

## Local services

- `backend`: FastAPI, PostgreSQL client and CPU-only PyTorch. The API image does not bundle the frontend. One Uvicorn worker is configured because session state and model memory are process-local.
- `frontend`: Node 22 Vite dev server with hot reload.
- `postgres`: PostgreSQL 17 for local/production engine parity.

`docker compose up --build` starts the services: `rodai-db` for PostgreSQL, `rodai-api` for FastAPI, and `rodai-frontend` for Vite. Apply migrations as an explicit operation before starting a new backend revision with `docker compose run --rm rodai-api alembic upgrade head`; app startup does not run migrations.

The local override enables a local-only benchmark library and mounts the root `datasets/` directory read-only at `/var/lib/rodai/datasets`. The directory contains only a catalog and instructions in Git; downloaded videos remain ignored and are never copied into the image or persistent upload storage. Add clips only after reviewing their dataset terms and use the `rights_reviewed` catalog field to keep unreviewed inputs unavailable. The library setting is rejected outside the `local` environment. See [`../datasets/README.md`](../datasets/README.md).

## Image details

Backend uses a multi-stage build with `python:3.12.8-slim-bookworm`; the frontend build stage uses `node:22.13.1-alpine3.21`. Production installs CPU-only PyTorch 2.14.1/torchvision 0.29.1 and `opencv-python-headless`, runs as a non-root user, writes app data to `/var/lib/rodai`, and logs to stdout/stderr. Model weights are not included.

These image tags are exact version tags, not digest-pinned. Image digests and final image sizes are not recorded because the Docker daemon is unavailable in the current environment; record both after a successful clean build before Phase 1 acceptance.

## Volumes and commands

Compose persists PostgreSQL data and RodAI data in separate named volumes. Video/export/model artifacts belong in the RodAI volume, never the container layer or PostgreSQL. Do not put datasets, checkpoints or secrets in the build context.

- Start backend + PostgreSQL: `scripts/run-backend.ps1`
- Start viewer + backend + PostgreSQL: `scripts/run-frontend.ps1`
- Tests: `scripts/run-tests.ps1`

These scripts require Docker Desktop's Linux-container daemon to be running.
