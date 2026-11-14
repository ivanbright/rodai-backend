# RodAI Project State

Updated: 2026-11-14

- **Current phase:** Phase 2 — video/session pipeline. Upload decoding, browser camera frame transport, session controls and frame-aligned JSONL exports are implemented. Phase 2 local checks passed; model inference remains a later phase.
- **Authorization:** The owner gave broad consent to begin and directed continued development. Earlier state documents did not record named phase approvals; retain the master prompt’s gates for material decisions.
- **Verified today:** PostgreSQL, API and Vite containers are running; API is healthy and the frontend serves HTTP 200; its `/api/v1/health` proxy returns healthy with database available. Alembic `0001_initial` is applied. Backend tests (9 passed), Ruff, frontend build, ESLint and Vitest (2 passed) pass. Synthetic video upload/result/deletion and browser camera websocket flows are covered by tests; upload smoke test ran against Docker.
- **Runtime:** Docker API uses Python 3.12.8 and PyTorch 2.14.1+cpu; CUDA is unavailable in that runtime, so CPU is selected. Host tests ran under Python 3.13.2, outside the package’s declared `>=3.12,<3.13` range.
- **Known issue:** `npm ci` reported 14 dependency vulnerabilities (2 low, 9 moderate, 1 high, 2 critical). `npm audit` could not retrieve advisory details because TLS certificate verification to `registry.npmjs.org` failed; investigate before deployment.
- **Next step:** Phase 3 detector integration requires choosing a model/package with reviewed license, sample footage and permissions, and confirming target camera context and available hardware. These remain unresolved; do not download weights or claim detector performance before then.

## Verified environment and project facts

- Workspace: `D:\rodai`; Docker Compose project name `rodai`.
- Node.js 22.13.0; host Python 3.13.2; container Python 3.12.8.
- Container health: `rodai-db` healthy, `rodai-api` healthy, `rodai-frontend` running. The frontend proxy reaches `/api/v1/health`.
- API health values: overall healthy, database available, device selected `cpu`, model unavailable, data volume available.
- Actual PyTorch runtime reports `2.14.1+cpu` and `torch.cuda.is_available() == False`.
- Alembic current revision: `0001_initial (head)`.
- Backend: pytest 4/4 passed; Ruff checks passed.
- Frontend: production build passed; ESLint passed; Vitest 1/1 passed.
- Git operations may need `-c safe.directory=D:/rodai` because repository ownership differs from the active Windows user.

## Not verified / outstanding

- Exact Windows edition, CPU model, installed RAM, GPU/VRAM and driver/CUDA on the host; target camera geometry; sample footage; local inference performance.
- Frontend dependency advisories (audit endpoint certificate failure).
- Detector package/weights choice and licenses; no model weights are installed.
- Phase 3 inference, tracking and model weights have not been implemented.
- Deployment-specific Railway plan, domain, audience, retention, privacy and public authentication decisions remain open.
