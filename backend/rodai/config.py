from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RODAI_", case_sensitive=False, populate_by_name=True
    )

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
    upload_retention_days: int = Field(7, ge=1, le=3650)
    results_retention_days: int = Field(30, ge=1, le=3650)
    exports_retention_days: int = Field(7, ge=1, le=3650)
    retention_sweep_interval_seconds: int = Field(3600, ge=60, le=86400)
    camera_max_width: int = Field(1280, ge=320, le=1280)
    camera_max_height: int = Field(720, ge=240, le=720)
    camera_jpeg_quality: float = Field(0.82, ge=0.5, le=0.95)
    device: Literal["auto", "cpu", "cuda"] = "cpu"
    detection_model: str = "unavailable"
    detection_model_revision: str = "70120ba84d68ca1211e007c4fb61d0cd5424be54"
    detection_threshold: float = Field(0.35, ge=0.05, le=0.99)
    inference_imgsz: int = Field(640, ge=128, le=2048)
    analysis_fps: float = Field(2.0, ge=1.0, le=15.0)
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
