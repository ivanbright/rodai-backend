import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rodai.benchmark_library import make_benchmark_router
from rodai.config import get_settings
from rodai.database import create_database_engine
from rodai.health import build_health
from rodai.retention import sweep_expired_artifacts
from rodai.sessions import (
    make_sessions_router,
    recover_interrupted_sessions,
    resume_interrupted_sessions,
    session_registry,
)

settings = get_settings()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(
    level=settings.log_level.upper(),
    handlers=[
        handler,
    ],
    force=True,
)
logger = logging.getLogger("rodai.backend")
engine = create_database_engine(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("RodAI backend starting environment=%s", settings.environment)
    recoveries = recover_interrupted_sessions(settings, engine, session_registry)
    recovery_task = asyncio.create_task(
        resume_interrupted_sessions(settings, engine, session_registry, recoveries)
    )

    async def expiry_loop() -> None:
        while True:
            try:
                counts = await asyncio.to_thread(sweep_expired_artifacts, settings, engine)
                if counts["deleted"] or counts["failed"]:
                    logger.info(
                        "Retention sweep deleted=%s failed=%s", counts["deleted"], counts["failed"]
                    )
            except Exception:
                logger.exception("Retention sweep failed")
            await asyncio.sleep(settings.retention_sweep_interval_seconds)

    retention_task = asyncio.create_task(expiry_loop())
    yield
    retention_task.cancel()
    recovery_task.cancel()
    try:
        await retention_task
    except asyncio.CancelledError:
        pass
    try:
        await recovery_task
    except asyncio.CancelledError:
        pass
    engine.dispose()
    logger.info("RodAI backend stopped")


app = FastAPI(title="RodAI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(make_sessions_router(settings, engine, session_registry))
app.include_router(make_benchmark_router(settings, engine, session_registry))


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, object]:
    return build_health(settings, engine)


@app.get("/api/v1/system", tags=["system"])
def system_status() -> dict[str, object]:
    return build_health(settings, engine)
