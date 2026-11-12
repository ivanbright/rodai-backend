from pathlib import Path

from rodai.config import Settings
from rodai.health import build_health


class UnavailableEngine:
    def connect(self) -> object:
        raise ConnectionError("fixture database unavailable")


def test_health_reports_real_unavailable_database_and_volume(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path, model_dir=tmp_path / "models")
    result = build_health(settings, UnavailableEngine())  # type: ignore[arg-type]
    assert result["status"] == "degraded"
    assert result["database"]["status"] == "unavailable"
    assert result["device"]["selected"] == "cpu"
    assert result["model"]["status"] == "unavailable"
    assert result["volume"]["status"] == "available"


def test_production_rejects_default_secret() -> None:
    try:
        Settings(environment="production")
    except ValueError as exc:
        assert "RODAI_SECRET_KEY" in str(exc)
    else:
        raise AssertionError("production accepted a development secret")
