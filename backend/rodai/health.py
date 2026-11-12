import shutil
from typing import Any

from sqlalchemy.engine import Engine

from rodai.config import Settings
from rodai.database import database_status


def runtime_device(configured_device: str) -> str:
    # No inference framework is installed in the foundation phase. Do not claim a GPU exists.
    return "cpu" if configured_device in {"auto", "cpu"} else "unavailable"


def build_health(settings: Settings, engine: Engine) -> dict[str, Any]:
    db_status, db_error = database_status(engine)
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

    healthy = db_status == "available" and volume["status"] == "available"
    return {
        "status": "healthy" if healthy else "degraded",
        "environment": settings.environment,
        "database": {"status": db_status, "error_type": db_error},
        "device": {"configured": settings.device, "selected": runtime_device(settings.device)},
        "model": {"status": "unavailable", "identifier": settings.detection_model},
        "volume": volume,
    }
