from __future__ import annotations

from typing import Any

from app.services.sprint.phase_detector import (
    detect_sprint_phases_v2,
)
from app.services.sprint.phase_metrics import (
    summarize_metrics_by_phase,
)
from app.services.sprint.phase_models import (
    SprintPhaseFrame,
    SprintSignalFrame,
)


def analyze_sprint_intelligence_v2(
    frames: list[SprintSignalFrame],
) -> dict[str, Any]:
    phase_result = detect_sprint_phases_v2(
        frames
    )

    if phase_result["status"] == "insufficient_data":
        return {
            "status": "insufficient_data",
            "phase_detection": phase_result,
            "phase_metrics": {
                "status": "insufficient_data",
                "phases": {},
            },
        }

    phase_frames = [
        SprintPhaseFrame(
            frame_index=item["frame_index"],
            timestamp_ms=item["timestamp_ms"],
            phase=item["phase"],
            confidence=item["confidence"],
            evidence=item["evidence"],
        )
        for item in phase_result["phase_frames"]
    ]

    phase_metrics = summarize_metrics_by_phase(
        frames,
        phase_frames,
    )

    return {
        "status": "experimental",
        "phase_detection": phase_result,
        "phase_metrics": phase_metrics,
        "engine_version": "2.0.0-phase1",
    }
