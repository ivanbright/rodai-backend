# Railway deployment (split frontend and API)

Railway is the target platform, but no Railway project, spend ceiling, plan approval or credentials are available in this workspace. The owner selected `rodai.cursorclick.dev` for planning and permits Railway's provided hostname as a temporary fallback. No DNS or domain configuration has been authorized. This is an implementation guide outline, not evidence that deployment has occurred. Do not provision paid resources or publish a public deployment until the owner approves the spend and Phase 1B is implemented and accepted.

## Target topology

Use three services in the Railway project: the existing `rodai-frontend` service built from `ivanbright/rodai-frontend`, a backend API service built from `ivanbright/rodai-backend`, and a Railway-managed PostgreSQL service. The frontend is served by its own small Node static server; the API image contains no frontend bundle. Point frontend `VITE_API_BASE_URL` to the backend's public HTTPS origin, and configure backend `RODAI_ALLOWED_ORIGINS` with the frontend's public origin(s). The intended frontend hostname is `https://rodai.cursorclick.dev`; attach it to the frontend service only after the approved Railway plan/budget and DNS steps are resolved. The API should use its Railway-provided public domain unless a separate API hostname is approved.

Mount a persistent volume on the API at `/var/lib/rodai`. Start with one API replica and one Uvicorn worker. Railway volumes currently prevent replicas and deployments from mounting the same service volume concurrently, so plan maintenance downtime and backup/rollback before upgrades. The first hosted release is invite-only with no self-registration, and supports uploaded video only; live browser-camera processing is local-only for now. Production inference is CPU-only.

## Variables

Railway scans root-level `.env` and `.env.<suffix>` files in the connected repository and offers their values as suggestions in the service Variables tab. Import root `.env.railway.example` into the API service. Import `.env.railway.example` from the frontend repository into the frontend service. `.env.example` files contain local-development values and must not be imported into production. Railway only suggests these values: import them into the matching service, replace placeholders, and review the staged changes. `VITE_API_BASE_URL` is embedded in Vite's frontend bundle at build time, so changes require a fresh frontend build/deploy; Railway notes that cached builds can retain previously embedded `VITE_*` values.

The API template references the PostgreSQL service by the name `Postgres`. Keep that service name or update the `${{Postgres.*}}` references to match the actual Railway database service name. `DATABASE_URL` includes the SQLAlchemy `+psycopg` driver required by this backend. Replace `RODAI_SECRET_KEY` with a newly generated secret before deploying; the committed local-only value intentionally fails production validation. Set `RODAI_ALLOWED_ORIGINS` to the frontend's exact public origin(s), comma-separated if using both a Railway-generated hostname and the custom hostname. Do not set `PORT`; Railway provides it. Never commit real credentials or secrets.

For the API service, use the Dockerfile builder with path `backend/Dockerfile`, leave Root Directory at `/`, and use the repository root as the build context. The API Dockerfile copies only `backend/`; it no longer needs the frontend submodule. For the frontend service, connect `ivanbright/rodai-frontend` on `main`, use root `/`, run `npm run build`, and start with `npm start`. The frontend's `server.mjs` serves `dist/` on Railway's `PORT` with SPA fallback routing.

## Ordered deployment steps (not yet executed)

1. Wait for the owner to approve a Railway plan and explicit monthly spend ceiling; set usage alerts/hard limits before provisioning paid resources.
2. Create PostgreSQL, API, and frontend services using their respective `main` branches. Enable Railway's wait-for-CI deployment gate for both code services.
3. Import the API and frontend variable templates into their matching services. Set the API origin in the frontend variable and create a fresh API secret.
4. Attach the API volume at `/var/lib/rodai`; confirm the service user can write it.
5. Configure database connectivity and verify the API service uses the root `railway.json`; its pre-deploy command runs `alembic upgrade head` before the new backend starts. Revision `0003_session_failure_details` adds a nullable error field and backfills failed-session diagnostics; take a database backup before deploying and retain the downgrade procedure.
6. Set `/api/v1/health` as the API health check, verify database/device/model/volume status, and test app + WebSocket behavior.
7. Only after separate approval, attach `rodai.cursorclick.dev` to the frontend and configure DNS; wait for TLS issuance, verify `https://` and `wss://`, and add its origin to API CORS.
8. Verify authenticated access, upload caps, retention/delete behavior, rate limits, logs, backup, volume persistence across redeploy, and rollback.

Railway's current docs say public WebSockets are supported and exempt from ordinary HTTP request-duration limits, while request bodies must finish within five minutes. The upload design therefore needs strict limits or chunked/resumable upload. Plan-specific CPU, RAM, storage limits and pricing change; re-check the current official plan documentation before choosing a plan. Current Railway volume behavior also limits an attached-volume service to one volume and disallows replicas.

## Rollback

Phase 1B must verify redeploying the prior Railway deployment and document the matching Alembic downgrade/backup procedure before the first app deployment is considered accepted. No rollback has been tested.
