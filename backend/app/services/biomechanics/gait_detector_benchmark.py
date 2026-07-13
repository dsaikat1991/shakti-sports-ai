from __future__ import annotations

from typing import Any

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_detector_config import (
    GaitDetectorConfig,
)
from app.services.biomechanics.gait_event_detector_v3 import (
    detect_gait_events_v3,
)
from app.services.biomechanics.gait_event_evaluator import (
    evaluate_by_event_type,
    evaluate_events,
)
from app.services.biomechanics.gait_event_models import (
    GaitEvent,
)


def _dict_to_event(item: dict[str, Any]) -> GaitEvent:
    return GaitEvent(
        event_type=item["event_type"],
        side=item["side"],
        timestamp_ms=int(item["timestamp_ms"]),
        frame_index=(
            int(item["frame_index"])
            if item.get("frame_index") is not None
            else None
        ),
        confidence=(
            float(item["confidence"])
            if item.get("confidence") is not None
            else None
        ),
        source=str(item.get("source", "v3")),
    )


def benchmark_detector_v3(
    frame_metrics: list[FrameMetrics],
    actual_events: list[GaitEvent],
    *,
    config: GaitDetectorConfig | None = None,
    tolerance_ms: int = 80,
) -> dict[str, Any]:
    detection = detect_gait_events_v3(
        frame_metrics,
        config=config,
        include_debug=False,
    )

    predicted_events = [
        _dict_to_event(item)
        for item in detection["events"]
    ]

    return {
        "detector": detection,
        "overall": evaluate_events(
            predicted_events,
            actual_events,
            tolerance_ms=tolerance_ms,
        ),
        "by_event_type": evaluate_by_event_type(
            predicted_events,
            actual_events,
            tolerance_ms=tolerance_ms,
        ),
    }
