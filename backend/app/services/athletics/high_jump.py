from __future__ import annotations

from typing import Any

from app.services.athletics.base import (
    AthleticsEventAnalyzer,
)
from app.services.athletics.models import (
    EventAnalysisRequest,
    EventAnalysisResult,
)


class HighJumpEventAnalyzer(AthleticsEventAnalyzer):
    event_name = "high_jump"
    analyzer_version = "0.1.0"

    def analyze(
        self,
        request: EventAnalysisRequest,
        *,
        core_biomechanics: dict[str, Any],
    ) -> EventAnalysisResult:
        readiness = {
            "ready": bool(
                core_biomechanics.get(
                    "status"
                ) == "completed"
            ),
            "required_camera_view": "Side or Rear-Quarter View",
            "bar_visible": None,
            "landing_mat_visible": None,
        }

        return EventAnalysisResult(
            event="high_jump",
            status=(
                "completed"
                if readiness["ready"]
                else "skipped"
            ),
            readiness=readiness,
            phases={
                "status": "planned",
                "supported": [],
                "target_phases": [
                    "approach",
                    "curve",
                    "penultimate_step",
                    "takeoff",
                    "bar_clearance",
                    "landing",
                ],
            },
            metrics={
                "core_biomechanics": core_biomechanics,
            },
            limitations=(
                "Bar detection is not yet implemented.",
                "True clearance height requires scene calibration.",
            ),
            analyzer_version=self.analyzer_version,
        )
