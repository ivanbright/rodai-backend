# Changelog

## Unreleased — Phase 0 documentation (2026-11-12)

- Added initial project state, decision proposals, assumptions, owner questions, and Phase 0 handover.
- Inspected the empty application workspace and recorded verified environment limitations.
- No application code or dependencies added; Phase 0 approval is pending.
- Incorporated `rodai-docker-railway-addendum.md` into the Phase 0 decision record and owner questions; verified current Railway resource, storage and networking documentation.

## Unreleased — Phase 1 foundation (2026-11-12)

- Added FastAPI health/system endpoints, Pydantic Settings, PostgreSQL connection status and initial Alembic metadata migration.
- Added CPU-only container build, Docker Compose services, environment example, React status viewer, tests and operations/security/privacy/licence docs.
- Docker runtime acceptance is pending: Docker daemon unavailable and frontend npm lockfile generation did not complete.

## Unreleased � Phase 1 verification and runtime status (2026-11-14)

- Verified Compose PostgreSQL, API and frontend startup; frontend API proxy returns healthy state with database available.
- Applied Alembic `0001_initial`; added PyTorch-backed CUDA availability detection with CPU fallback and unavailable reporting for requested CUDA when absent.
- Added API health dependency ordering for the Compose frontend and ignored local pip cache/temp directories.
- Backend pytest (4 passed), Ruff, frontend production build, ESLint and Vitest (1 passed) pass. Host pytest ran on Python 3.13.2; Docker API image uses Python 3.12.8.
- `npm ci` reported 14 dependency vulnerabilities; advisory lookup via `npm audit` failed TLS certificate verification and remains unresolved.
- Video input, sessions, detector inference and model weights remain unimplemented.

## Unreleased — Phase 0 owner decisions reconciled (2026-11-14)

- Recorded the owner's Rwanda/Kigali target, privacy/retention defaults, commercial licensing constraint, isolated Python 3.12 environment, PostgreSQL requirement, transport/concurrency settings, Railway topology, invite-only access, planned domain, and deployment spending gate.
- Updated Phase 0 architecture and remaining questions. The owner explicitly withheld Phase 0 approval; no new implementation phase is authorized.
- Flagged current conformance gaps: automated retention and configurable 1280x720/JPEG capture controls are not implemented.
