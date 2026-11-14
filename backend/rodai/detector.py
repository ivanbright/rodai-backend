"""Local CPU-capable DETR inference with a deliberately small detection contract."""

from __future__ import annotations

import logging
import threading
from typing import Any

import cv2
import numpy as np

from rodai.config import Settings

logger = logging.getLogger("rodai.detector")
ROAD_CLASSES = frozenset({"person", "bicycle", "motorcycle", "car", "bus", "truck"})


class DetrDetector:
    def __init__(self, settings: Settings) -> None:
        import torch
        from transformers import AutoImageProcessor, AutoModelForObjectDetection

        self._torch = torch
        self._processor = AutoImageProcessor.from_pretrained(
            settings.detection_model,
            revision=settings.detection_model_revision,
            cache_dir=settings.model_dir,
        )
        self._model = AutoModelForObjectDetection.from_pretrained(
            settings.detection_model,
            revision=settings.detection_model_revision,
            cache_dir=settings.model_dir,
        ).to("cpu")
        self._model.eval()
        self._threshold = settings.detection_threshold
        self._lock = threading.Lock()

    def __call__(self, frame: np.ndarray) -> list[dict[str, Any]]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self._processor(images=rgb, return_tensors="pt")
        with self._lock, self._torch.inference_mode():
            outputs = self._model(**image)
        height, width = frame.shape[:2]
        result = self._processor.post_process_object_detection(
            outputs,
            target_sizes=self._torch.tensor([[height, width]]),
            threshold=self._threshold,
        )[0]
        detections: list[dict[str, Any]] = []
        for score, class_id, box in zip(
            result["scores"], result["labels"], result["boxes"], strict=True
        ):
            label_id = int(class_id.item())
            label = str(self._model.config.id2label.get(label_id, label_id)).lower()
            if label not in ROAD_CLASSES:
                continue
            x1, y1, x2, y2 = (round(float(value), 2) for value in box.tolist())
            detections.append(
                {
                    "class_id": label_id,
                    "label": label,
                    "confidence": round(float(score.item()), 4),
                    "bbox_xyxy": [x1, y1, x2, y2],
                }
            )
        return detections


_instances: dict[tuple[str, str, str], DetrDetector] = {}
_instances_lock = threading.Lock()
_statuses: dict[tuple[str, str, str], dict[str, str]] = {}


def get_detector(settings: Settings) -> DetrDetector | None:
    if settings.detection_model == "unavailable":
        return None
    key = (settings.detection_model, settings.detection_model_revision, str(settings.model_dir))
    with _instances_lock:
        if key not in _instances:
            _statuses[key] = {"status": "loading", "error": ""}
            logger.info("Loading detector model=%s revision=%s", key[0], key[1])
            try:
                _instances[key] = DetrDetector(settings)
            except Exception as exc:
                _statuses[key] = {"status": "failed", "error": type(exc).__name__}
                raise
            _statuses[key] = {"status": "available", "error": ""}
            logger.info("Detector ready model=%s", key[0])
        return _instances[key]


def health_status(settings: Settings) -> dict[str, str]:
    if settings.detection_model == "unavailable":
        return {"status": "unavailable", "identifier": settings.detection_model}
    key = (settings.detection_model, settings.detection_model_revision, str(settings.model_dir))
    state = _statuses.get(key, {"status": "not_loaded", "error": ""})
    return {
        "status": state["status"],
        "identifier": settings.detection_model,
        "error_type": state["error"] or None,
    }
