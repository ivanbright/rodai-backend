from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from rodai.config import Settings


def create_database_engine(settings: Settings) -> Engine:
    return create_engine(settings.database_url, pool_pre_ping=True, pool_size=5, max_overflow=5)


def database_status(engine: Engine) -> tuple[str, str | None]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "available", None
    except Exception as exc:  # health must report dependency failures without exposing internals
        return "unavailable", type(exc).__name__
