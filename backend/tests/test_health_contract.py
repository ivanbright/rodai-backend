import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from rodai.config import Settings
from rodai.health import build_health, runtime_device


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


def test_auto_device_uses_cuda_only_when_runtime_reports_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A small fake runtime isolates device selection from the host's actual hardware.
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: True))
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    assert runtime_device("auto") == "cuda"


def test_explicit_cuda_is_unavailable_when_runtime_has_no_cuda(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    assert runtime_device("cuda") == "unavailable"
