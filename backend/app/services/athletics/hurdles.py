from __future__ import annotations

from typing import Any

from app.services.athletics.base import (
    AthleticsEventAnalyzer,
)
from app.services.athletics.models import (
    EventAnalysisRequest,
    EventAnalysisResult,
)


class HurdlesEventAnalyzer(AthleticsEventAnalyzer):
    event_name = "hurdles"
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
            "required_camera_view": "Side View",
            "hurdle_visible": None,
        }

        return EventAnalysisResult(
            event="hurdles",
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
                    "takeoff",
                    "lead_leg_clearance",
                    "trail_leg_clearance",
                    "landing",
                    "inter_hurdle_sprint",
                ],
            },
            metrics={
                "core_biomechanics": core_biomechanics,
            },
            limitations=(
                "Hurdle-object detection is not yet implemented.",
                "Lead-leg and trail-leg classification is not yet implemented.",
            ),
            analyzer_version=self.analyzer_version,
        )
