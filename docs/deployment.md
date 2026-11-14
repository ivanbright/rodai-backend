# Railway deployment (Phase 1B pending)

Railway is the target platform, but no Railway project, spend ceiling, plan approval or credentials are available in this workspace. The owner selected `rodai.cursorclick.dev` for planning and permits Railway's provided hostname as a temporary fallback. No DNS or domain configuration has been authorized. This is an implementation guide outline, not evidence that deployment has occurred. Do not provision paid resources or publish a public deployment until the owner approves the spend and Phase 1B is implemented and accepted.

## Target topology

One Dockerfile-based `rodai-app` service serves the built frontend and FastAPI from the same origin. Add a Railway-managed PostgreSQL service and a persistent volume mounted at `/var/lib/rodai`. Start with one app replica and one Uvicorn worker. Railway volumes currently prevent replicas and deployments from mounting the same service volume concurrently, so plan maintenance downtime and backup/rollback before upgrades. The first hosted release is invite-only with no self-registration, and supports uploaded video only; live browser-camera processing is local-only for now. Production inference is CPU-only.

## Variables

Railway scans root-level `.env` and `.env.<suffix>` files in the connected repository and offers their values as suggestions in the service Variables tab. Use the root-level `.env.railway.example` for the RodAI service; `.env.example` contains local-development values and must not be imported into production. Railway only suggests these values: import them in the app service's Variables tab and review the staged changes.

The template references the PostgreSQL service by the name `Postgres`. Keep that service name or update the `${{Postgres.*}}` references to match the actual Railway database service name. `DATABASE_URL` includes the SQLAlchemy `+psycopg` driver required by this backend. Replace `RODAI_SECRET_KEY` with a newly generated secret before deploying; the committed local-only value intentionally fails production validation. Do not set `PORT`; Railway provides it. Never commit real credentials or secrets.

The repository uses `frontend` as a Git submodule and the Dockerfile needs the repository root as its build context. Set the service Dockerfile path to `backend/Dockerfile`, leave the root directory at `/`, and confirm Railway checks out the submodule. The template includes Railway's recursive clone setting for this submodule.

## Ordered deployment steps (not yet executed)

1. Wait for the owner to approve a Railway plan and explicit monthly spend ceiling; set usage alerts/hard limits before provisioning paid resources.
2. Create the PostgreSQL service and app service from the repository's `main` branch using the Dockerfile. Enable Railway's wait-for-CI deployment gate.
3. Attach the app volume at `/var/lib/rodai`; confirm the service user can write it.
4. Configure environment variables and database connectivity. Run Alembic migration as an explicit release step with documented rollback.
5. Set `/api/v1/health` as the health check, verify database/device/model/volume status, and test app + WebSocket behavior.
6. Only after separate approval, configure the owner-provided `rodai.cursorclick.dev` domain/DNS, wait for TLS issuance, verify `https://` and `wss://`.
7. Verify authenticated access, upload caps, retention/delete behavior, rate limits, logs, backup, volume persistence across redeploy, and rollback.

Railway's current docs say public WebSockets are supported and exempt from ordinary HTTP request-duration limits, while request bodies must finish within five minutes. The upload design therefore needs strict limits or chunked/resumable upload. Plan-specific CPU, RAM, storage limits and pricing change; re-check the current official plan documentation before choosing a plan. Current Railway volume behavior also limits an attached-volume service to one volume and disallows replicas.

## Rollback

Phase 1B must verify redeploying the prior Railway deployment and document the matching Alembic downgrade/backup procedure before the first app deployment is considered accepted. No rollback has been tested.
