# RodAI Phase 1 Handover — Foundation

Date: 2026-11-12  
Status: **In progress; acceptance criteria unmet.** User authorized project start; this handover does not claim Phase 1 complete.

## Implemented

- FastAPI app titled `RodAI API`, versioned health/system routes.
- Pydantic Settings with environment-prefix configuration and production secret/database validation.
- Health reports database connectivity, configured/selected CPU device, model unavailable state, and data-volume capacity without exposing the absolute path.
- PostgreSQL engine, explicit Alembic setup and initial metadata migration for sources, sessions, results, events and model registry.
- React/TypeScript/Vite status viewer; backend-disconnected state is explicit and no AI output is fabricated.
- Multi-stage Dockerfile, Docker Compose for backend/frontend/PostgreSQL, `.dockerignore`, `.gitignore`, `.env.example`, PowerShell run/test scripts.
- Setup, Docker, deployment, security, privacy and preliminary licence documentation.
- Initialized a Git repository. Git status/staging could not be completed because Git rejected the workspace ownership as dubious; current user is `IVANBRIGHT/CodexSandboxOffline`, repository owner is `IVANBRIGHT/Bright`.
- Added a separate frontend repository at `IvanBright/Rodai-frontend`; initial checkpoint `b088ba7` was pushed to GitHub's canonical `ivanbright/rodai-frontend` remote. Root repository is intended to reference it as a submodule.

## Dependencies

Pinned candidates: FastAPI 0.115.8, Uvicorn 0.34.0, Pydantic Settings 2.7.1, SQLAlchemy 2.0.38, psycopg 3.2.4, Alembic 1.14.1, PyYAML 6.0.2, OpenCV headless 4.11.0.86, PyTorch 2.14.1 CPU / torchvision 0.29.1, React 19.0.0, Vite 6.1.0, TypeScript 5.7.3, Node 22.13.1. Backend dependency versions are pinned in project files, but not resolved/installed/verified. `frontend/package-lock.json` is missing.

## Verification performed and actual output

- `python -m compileall -q .\backend\rodai .\backend\migrations .\backend\tests` → exit code 0.
- `docker ps` → `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ... The system cannot find the file specified.` Docker Desktop daemon is not running/reachable.
- `npm.cmd install --package-lock-only --ignore-scripts --no-audit --no-fund` produced no output for over a minute and was interrupted. Offline retry returned `npm error code ENOTCACHED` for `@testing-library/react`; no package lock was generated.
- `git init` → initialized the root repository. Initial status required a workspace-scoped `safe.directory` setting because Git reported different sandbox/repository owners.
- Frontend `git init`, commit `b088ba7` (`chore(frontend): add RodAI foundation viewer`), origin configuration and push all succeeded. GitHub redirected the mixed-case URL to `https://github.com/ivanbright/rodai-frontend.git`.
- Backend remote check for `https://github.com/IvanBright/Rodai.git` returned `Repository not found`; it may be private or the repository URL/name may differ. No backend remote was added and no backend commit was pushed yet.
- No Compose build, service start, Alembic migration, automated test, frontend build, lint, or image-size inspection ran.

## What works / not established

Python files are syntactically compilable. Actual startup, database connectivity, settings parsing in Pydantic, frontend build, migration execution and test outcomes are unverified because dependencies and Docker services could not be run.

## Known limitations and unmet acceptance criteria

- `frontend/package-lock.json` is required by `npm ci` in the Dockerfile but absent; the image build will fail until the lock is generated.
- Docker daemon is unavailable, so the required clean-clone `docker compose up`, container tests, health checks and image-size/digest measurements were not demonstrated.
- Docker base tags are pinned but digests are not recorded.
- No authentication is implemented; this foundation must not be exposed publicly. Authentication and Railway deployment belong to Phase 1B.
- No Docker build/run/test results exist, so Phase 1 acceptance criteria are unmet and this phase is not complete.
- Root/backend repo still needs its commit and verified origin. Frontend initial commit is pushed but the generated package lock is still pending.

## Decisions needed / recommended next step

Resolve the local Docker daemon and npm registry access; generate the frontend lockfile; build the image, start the stack, run migrations, backend/frontend tests and linters inside containers, record image digest/size, then update this handover with actual output. Only after Phase 1 acceptance passes should work move to Phase 1B.

Before deployment/benchmark phases, confirm Railway plan/budget, domain/DNS, user audience, retention, upload size/duration, public camera need, detector licensing and hardware. No detector or weights are selected, and exact dependency/transitive licences still require release review.
