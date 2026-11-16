"""Read-only registry for owner-supplied, locally stored benchmark clips."""

from __future__ import annotations

import json
import logging
import mimetypes
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import Engine

from rodai.config import Settings
from rodai.retention import register_artifact
from rodai.sessions import (
    SessionRegistry,
    SessionState,
    _create_database_session,
    _delete_session_records,
    _process_video,
)

logger = logging.getLogger("rodai.benchmark_library")
VIDEO_SUFFIXES = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
MAX_CATALOG_BYTES = 2 * 1024 * 1024


class BenchmarkClip(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str = Field(min_length=1, max_length=160)
    file: str = Field(min_length=1, max_length=512)
    rights_reviewed: bool = False
    source_url: str
    license_name: str = Field(min_length=1, max_length=160)
    permitted_uses: str = Field(min_length=1, max_length=300)
    creator_attribution: str | None = Field(default=None, max_length=240)
    privacy_reviewed: bool = False
    event_type: str = Field(default="unlabeled", min_length=1, max_length=64)
    event_time_seconds: float | None = Field(default=None, ge=0)
    annotation_reference: str | None = Field(default=None, max_length=512)
    split: str | None = Field(default=None, max_length=32)

    @field_validator("id")
    @classmethod
    def valid_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("IDs may contain lowercase letters, digits, and hyphens only")
        return value

    @field_validator("source_url")
    @classmethod
    def safe_source_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Source URLs must use HTTP or HTTPS")
        return value

    @field_validator("file")
    @classmethod
    def safe_relative_file(cls, value: str) -> str:
        if "\\" in value or value.startswith("/") or ":" in value:
            raise ValueError("Clip file paths must be relative POSIX paths")
        parts = Path(value).parts
        if not parts or any(part in {"", ".", ".."} for part in parts):
            raise ValueError("Clip file paths cannot contain traversal segments")
        if Path(value).suffix.lower() not in VIDEO_SUFFIXES:
            raise ValueError("Clip file must use a supported video extension")
        return value


class BenchmarkDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1, max_length=160)
    camera_view: str = Field(min_length=1, max_length=120)
    source_url: str
    terms_url: str
    license_name: str = Field(min_length=1, max_length=160)
    purpose: str = Field(min_length=1, max_length=500)
    limitation: str = Field(min_length=1, max_length=500)
    clips: list[BenchmarkClip] = Field(default_factory=list, max_length=2000)

    @field_validator("id")
    @classmethod
    def valid_id(cls, value: str) -> str:
        if not SAFE_ID.fullmatch(value):
            raise ValueError("IDs may contain lowercase letters, digits, and hyphens only")
        return value

    @field_validator("source_url", "terms_url")
    @classmethod
    def safe_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Dataset links must use HTTP or HTTPS")
        return value

    @model_validator(mode="after")
    def unique_clip_ids(self) -> BenchmarkDataset:
        ids = [clip.id for clip in self.clips]
        if len(ids) != len(set(ids)):
            raise ValueError("Clip IDs must be unique within a dataset")
        return self


class BenchmarkCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1, le=1)
    datasets: list[BenchmarkDataset] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def unique_dataset_ids(self) -> BenchmarkCatalog:
        ids = [dataset.id for dataset in self.datasets]
        if len(ids) != len(set(ids)):
            raise ValueError("Dataset IDs must be unique")
        return self


def load_catalog(dataset_dir: Path) -> BenchmarkCatalog:
    catalog_path = dataset_dir / "catalog.json"
    try:
        if catalog_path.stat().st_size > MAX_CATALOG_BYTES:
            raise ValueError("Benchmark catalog exceeds the 2 MB limit")
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
        return BenchmarkCatalog.model_validate(raw)
    except FileNotFoundError as exc:
        raise HTTPException(503, "Local benchmark catalog.json is not mounted.") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        logger.warning("Benchmark catalog could not be read: %s", type(exc).__name__)
        raise HTTPException(503, "Local benchmark catalog is invalid or unavailable.") from exc


def clip_path(dataset_dir: Path, dataset: BenchmarkDataset, clip: BenchmarkClip) -> Path:
    root = dataset_dir.resolve()
    target = (root / dataset.id / clip.file).resolve()
    if root not in target.parents:
        raise HTTPException(400, "Benchmark clip path escapes the local library.")
    return target


def find_clip(
    dataset_dir: Path, dataset_id: str, clip_id: str
) -> tuple[BenchmarkDataset, BenchmarkClip, Path]:
    catalog = load_catalog(dataset_dir)
    dataset = next((item for item in catalog.datasets if item.id == dataset_id), None)
    if dataset is None:
        raise HTTPException(404, "Benchmark dataset not found.")
    clip = next((item for item in dataset.clips if item.id == clip_id), None)
    if clip is None:
        raise HTTPException(404, "Benchmark clip not found.")
    if not clip.rights_reviewed:
        raise HTTPException(403, "Review and record permission for this clip before using it.")
    path = clip_path(dataset_dir, dataset, clip)
    if not path.is_file():
        raise HTTPException(404, "The registered benchmark video file is not present locally.")
    return dataset, clip, path


def public_clip(
    dataset_dir: Path, dataset: BenchmarkDataset, clip: BenchmarkClip
) -> dict[str, Any]:
    path = clip_path(dataset_dir, dataset, clip)
    exists = path.is_file()
    return {
        **clip.model_dump(),
        "file_available": exists,
        "can_analyze": exists and clip.rights_reviewed,
        "size_bytes": path.stat().st_size if exists else None,
        "video_url": (
            f"/api/v1/benchmarks/{dataset.id}/clips/{clip.id}/video"
            if exists and clip.rights_reviewed
            else None
        ),
    }


def source_metadata(
    dataset: BenchmarkDataset, clip: BenchmarkClip, path: Path, dataset_dir: Path
) -> dict[str, Any]:
    return {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "clip_id": clip.id,
        "title": clip.title,
        "relative_file": path.resolve().relative_to(dataset_dir.resolve()).as_posix(),
        "source_url": clip.source_url,
        "license_name": clip.license_name,
        "permitted_uses": clip.permitted_uses,
        "creator_attribution": clip.creator_attribution,
        "privacy_reviewed": clip.privacy_reviewed,
        "event_type": clip.event_type,
        "event_time_seconds": clip.event_time_seconds,
        "annotation_reference": clip.annotation_reference,
        "split": clip.split,
    }


def make_benchmark_router(
    settings: Settings, engine: Engine, registry: SessionRegistry
) -> APIRouter:
    """Expose a local-only catalog and direct analysis of reviewed clips."""
    router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])

    @router.get("")
    def get_benchmarks() -> dict[str, Any]:
        if not settings.dataset_library_enabled:
            return {"enabled": False, "local_only": True, "datasets": []}
        catalog = load_catalog(settings.dataset_dir)
        datasets: list[dict[str, Any]] = []
        for dataset in catalog.datasets:
            datasets.append(
                {
                    **dataset.model_dump(exclude={"clips"}),
                    "clips": [
                        public_clip(settings.dataset_dir, dataset, clip)
                        for clip in dataset.clips
                    ],
                }
            )
        return {"enabled": True, "local_only": True, "datasets": datasets}

    @router.get("/{dataset_id}/clips/{clip_id}/video")
    def get_benchmark_video(dataset_id: str, clip_id: str) -> FileResponse:
        if not settings.dataset_library_enabled:
            raise HTTPException(404, "The local benchmark library is disabled.")
        _, _, path = find_clip(settings.dataset_dir, dataset_id, clip_id)
        return FileResponse(
            path,
            media_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            filename=path.name,
            content_disposition_type="inline",
        )

    @router.post(
        "/{dataset_id}/clips/{clip_id}/analyze", status_code=status.HTTP_202_ACCEPTED
    )
    def analyze_benchmark_video(
        dataset_id: str,
        clip_id: str,
        background_tasks: BackgroundTasks,
        analysis_fps: float | None = Query(default=None, ge=1.0, le=15.0),
    ) -> dict[str, Any]:
        if not settings.dataset_library_enabled:
            raise HTTPException(404, "The local benchmark library is disabled.")

        dataset, clip, path = find_clip(settings.dataset_dir, dataset_id, clip_id)
        session_id = str(uuid4())
        fps = analysis_fps or settings.analysis_fps
        benchmark = source_metadata(dataset, clip, path, settings.dataset_dir)
        state = SessionState(
            id=session_id,
            filename=clip.title,
            status="queued",
            created_at=datetime.now(UTC).isoformat(),
            uploaded_bytes=path.stat().st_size,
            source_type="benchmark_video",
            analysis_fps=fps,
            benchmark={key: value for key, value in benchmark.items() if key != "relative_file"},
        )
        try:
            registry.add(state, settings.max_concurrent_sessions)
        except RuntimeError as exc:
            raise HTTPException(409, str(exc)) from exc

        result_path = settings.data_dir / "sessions" / session_id / "results.jsonl"
        try:
            result_path.parent.mkdir(parents=True, exist_ok=True)
            _create_database_session(
                engine,
                session_id,
                source_type="benchmark_video",
                source_metadata=benchmark,
                analysis_fps=fps,
            )
            register_artifact(
                engine,
                session_id=session_id,
                artifact_type="session",
                relative_path=None,
                retention_days=settings.results_retention_days,
            )
        except Exception as exc:
            _delete_session_records(engine, session_id)
            registry.remove(session_id)
            shutil.rmtree(result_path.parent, ignore_errors=True)
            logger.exception("Could not start benchmark analysis session")
            raise HTTPException(503, "Could not create a benchmark analysis session.") from exc

        background_tasks.add_task(
            _process_video,
            engine,
            settings,
            registry,
            session_id,
            path,
            result_path,
            analysis_fps=fps,
        )
        return state.response()

    return router
