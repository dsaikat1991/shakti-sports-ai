from __future__ import annotations

from typing import Any

from app.services.athletics.base import (
    AthleticsEventAnalyzer,
)
from app.services.athletics.models import (
    EventAnalysisRequest,
    EventAnalysisResult,
)


class LongJumpEventAnalyzer(AthleticsEventAnalyzer):
    event_name = "long_jump"
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
            "takeoff_board_visible": None,
            "landing_area_visible": None,
        }

        return EventAnalysisResult(
            event="long_jump",
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
                    "penultimate_step",
                    "final_step",
                    "takeoff",
                    "flight",
                    "landing",
                ],
            },
            metrics={
                "core_biomechanics": core_biomechanics,
            },
            limitations=(
                "Takeoff-board detection is not yet implemented.",
                "Jump distance cannot be estimated without scene calibration.",
            ),
            analyzer_version=self.analyzer_version,
        )
