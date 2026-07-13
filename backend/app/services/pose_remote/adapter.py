from __future__ import annotations

from typing import Any


def to_shakti_landmarks(worker_response: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "track_id": instance.get("track_id"),
            "confidence": instance.get("confidence", 0.0),
            "provider": "rtmpose",
            "source_schema": instance.get("source_schema"),
            "bounding_box": instance.get("bounding_box"),
            "detector_fallback": instance.get("detector_fallback", False),
            "landmarks": instance.get("keypoints", {}),
        }
        for instance in worker_response.get("instances", [])
    ]
