from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RODAI_", case_sensitive=False, populate_by_name=True)

    environment: Literal["local", "staging", "production"] = Field("local", alias="RODAI_ENV")
    port: int = Field(8000, alias="PORT", ge=1, le=65535)
    database_url: str = Field(
        "postgresql+psycopg://rodai:rodai-local-only@localhost:5432/rodai",
        alias="DATABASE_URL",
    )
    data_dir: Path = Field(Path("./data"), alias="RODAI_DATA_DIR")
    model_dir: Path = Field(Path("./data/models"), alias="RODAI_MODEL_DIR")
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    secret_key: SecretStr = Field(SecretStr("local-development-only-change-before-deploy"))
    max_upload_mb: int = Field(500, ge=1, le=50_000)
    max_video_seconds: int = Field(600, ge=1, le=86_400)
    max_concurrent_sessions: int = Field(1, ge=1, le=8)
    device: Literal["auto", "cpu", "cuda"] = "cpu"
    detection_model: str = "unavailable"
    inference_imgsz: int = Field(640, ge=128, le=2048)
    log_level: str = "INFO"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_deployment_secrets(self) -> "Settings":
        if self.environment == "production":
            if self.secret_key.get_secret_value() == "local-development-only-change-before-deploy":
                raise ValueError("RODAI_SECRET_KEY must be set to a unique secret in production")
            if "local-only" in self.database_url or "localhost" in self.database_url:
                raise ValueError("DATABASE_URL must point to the production database")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
