from __future__ import annotations

from typing import Any

from app.services.athletics.base import (
    AthleticsEventAnalyzer,
)
from app.services.athletics.models import (
    EventAnalysisRequest,
    EventAnalysisResult,
)
from app.services.athletics.sprint_phase import (
    detect_sprint_phases,
)


def _extract_phase_inputs(
    core_biomechanics: dict[str, Any],
) -> tuple[list[int], list[float]]:
    timeline = core_biomechanics.get(
        "motion_timeline",
        [],
    )

    timestamps: list[int] = []
    progression: list[float] = []

    for item in timeline:
        timestamp = item.get(
            "timestamp_ms"
        )
        horizontal = item.get(
            "horizontal_progression"
        )

        if not isinstance(
            timestamp,
            int,
        ):
            continue

        if not isinstance(
            horizontal,
            (int, float),
        ):
            continue

        timestamps.append(timestamp)
        progression.append(
            float(horizontal)
        )

    return timestamps, progression


class SprintEventAnalyzer(AthleticsEventAnalyzer):
    event_name = "sprint"
    analyzer_version = "0.2.0"

    def analyze(
        self,
        request: EventAnalysisRequest,
        *,
        core_biomechanics: dict[str, Any],
    ) -> EventAnalysisResult:
        ready = bool(
            core_biomechanics.get(
                "status"
            ) == "completed"
        )

        readiness = {
            "ready": ready,
            "required_camera_view": (
                "Side View"
            ),
        }

        if ready:
            timestamps, progression = (
                _extract_phase_inputs(
                    core_biomechanics
                )
            )

            phases = detect_sprint_phases(
                timestamps_ms=timestamps,
                horizontal_progression=progression,
            )
        else:
            phases = {
                "status": "not_analyzed",
                "phases": [],
            }

        return EventAnalysisResult(
            event="sprint",
            status=(
                "completed"
                if ready
                else "skipped"
            ),
            readiness=readiness,
            phases=phases,
            metrics={
                "core_biomechanics": (
                    core_biomechanics
                ),
            },
            limitations=(
                "Sprint phase segmentation remains experimental.",
                "Reaction and block exit require dedicated start detection.",
            ),
            analyzer_version=self.analyzer_version,
        )
