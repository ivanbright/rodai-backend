import logging
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from rodai.config import get_settings
from rodai.database import create_database_engine
from rodai.health import build_health

settings = get_settings()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=settings.log_level.upper(), handlers=[handler,], force=True)
logger = logging.getLogger("rodai.backend")
engine = create_database_engine(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("RodAI backend starting environment=%s", settings.environment)
    yield
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


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, object]:
    return build_health(settings, engine)


@app.get("/api/v1/system", tags=["system"])
def system_status() -> dict[str, object]:
    return build_health(settings, engine)


frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        requested = (frontend_dist / path).resolve()
        if frontend_dist.resolve() not in requested.parents:
            requested = frontend_dist / "index.html"
        if not requested.is_file():
            requested = frontend_dist / "index.html"
        return FileResponse(requested)
