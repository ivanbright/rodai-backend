import shutil
from typing import Any

from sqlalchemy.engine import Engine

from rodai.config import Settings
from rodai.database import database_status
from rodai.detector import health_status
from rodai.retention import retention_status


def runtime_device(configured_device: str) -> str:
    """Return the device available to the inference runtime, without guessing hardware."""
    try:
        import torch
    except ImportError:
        return "cpu" if configured_device in {"auto", "cpu"} else "unavailable"

    cuda_available = torch.cuda.is_available()
    if configured_device == "cuda":
        return "cuda" if cuda_available else "unavailable"
    if configured_device == "auto":
        return "cuda" if cuda_available else "cpu"
    return "cpu"


def build_health(settings: Settings, engine: Engine) -> dict[str, Any]:
    db_status, db_error = database_status(engine)
    retention = retention_status(engine)
    try:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        total, used, free = shutil.disk_usage(settings.data_dir)
        volume: dict[str, Any] = {
            "status": "available",
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
        }
    except OSError as exc:
        volume = {"status": "unavailable", "error": type(exc).__name__}

    healthy = (
        db_status == "available"
        and volume["status"] == "available"
        and retention["status"] == "available"
        and retention["failed_deletions"] == 0
    )
    return {
        "status": "healthy" if healthy else "degraded",
        "environment": settings.environment,
        "database": {"status": db_status, "error_type": db_error},
        "device": {"configured": settings.device, "selected": runtime_device(settings.device)},
        "model": health_status(settings),
        "retention": retention,
        "volume": volume,
    }
