# Railway deployment (Phase 1B pending)

Railway is the target platform, but no Railway project, domain, plan or credentials are available in this workspace. This is an implementation guide outline, not evidence that deployment has occurred. Do not publish a public deployment until Phase 1B is implemented and accepted.

## Target topology

One Dockerfile-based `rodai-app` service serves the built frontend and FastAPI from the same origin. Add a Railway-managed PostgreSQL service and a persistent volume mounted at `/var/lib/rodai`. Start with one app replica and one Uvicorn worker. Railway volumes currently prevent replicas and deployments from mounting the same service volume concurrently, so plan maintenance downtime and backup/rollback before upgrades.

## Variables

Configure the variables listed in `.env.example` in Railway service settings. Set `PORT` from Railway, `DATABASE_URL` using the Railway PostgreSQL private connection URL, unique `RODAI_SECRET_KEY`, HTTPS origin allow-list, production data/model paths, upload/duration/concurrency limits, CPU device, model ID and log level. Never store credentials in Git or images.

## Ordered deployment steps (not yet executed)

1. Create/select the Railway workspace and plan within the owner-approved monthly budget; set usage alerts/hard limits.
2. Create the PostgreSQL service and app service from the repository using the Dockerfile.
3. Attach the app volume at `/var/lib/rodai`; confirm the service user can write it.
4. Configure environment variables and database connectivity. Run Alembic migration as an explicit release step with documented rollback.
5. Set `/api/v1/health` as the health check, verify database/device/model/volume status, and test app + WebSocket behavior.
6. Add the owner-provided domain, configure DNS at its provider, wait for TLS issuance, verify `https://` and `wss://`.
7. Verify authenticated access, upload caps, retention/delete behavior, rate limits, logs, backup, volume persistence across redeploy, and rollback.

Railway's current docs say public WebSockets are supported and exempt from ordinary HTTP request-duration limits, while request bodies must finish within five minutes. The upload design therefore needs strict limits or chunked/resumable upload. Plan-specific CPU, RAM, storage limits and pricing change; re-check the current official plan documentation before choosing a plan. Current Railway volume behavior also limits an attached-volume service to one volume and disallows replicas.

## Rollback

Phase 1B must verify redeploying the prior Railway deployment and document the matching Alembic downgrade/backup procedure before the first app deployment is considered accepted. No rollback has been tested.
