from __future__ import annotations

from typing import Any

from app.services.digital_twin.fatigue import (
    detect_longitudinal_fatigue_pattern,
)
from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
)
from app.services.digital_twin.personal_bests import (
    build_personal_best_map,
)
from app.services.digital_twin.plateau import (
    detect_plateau,
)
from app.services.digital_twin.trends import (
    build_trend_map,
)


DEFAULT_TRACKED_METRICS = [
    "mechanical_efficiency_score",
    "front_side_score",
    "back_side_score",
    "ground_contact_ms",
    "cadence_spm",
    "symmetry_score",
    "vertical_oscillation_percent",
]


def build_digital_twin_summary(
    snapshots: list[AthleteMetricSnapshot],
    *,
    tracked_metrics: list[str] | None = None,
) -> dict[str, Any]:
    if not snapshots:
        return {
            "status": "insufficient_data",
        }

    ordered = sorted(
        snapshots,
        key=lambda item: item.recorded_at,
    )

    metrics = (
        tracked_metrics
        or DEFAULT_TRACKED_METRICS
    )

    plateaus = {
        metric_name: detect_plateau(
            ordered,
            metric_name=metric_name,
        )
        for metric_name in metrics
    }

    return {
        "status": "experimental",
        "athlete_id": (
            ordered[-1].athlete_id
        ),
        "event": ordered[-1].event,
        "sessions_analyzed": len(
            ordered
        ),
        "first_recorded_at": (
            ordered[0].recorded_at
        ),
        "latest_recorded_at": (
            ordered[-1].recorded_at
        ),
        "latest_performance_id": (
            ordered[-1].performance_id
        ),
        "trends": build_trend_map(
            ordered,
            metrics=metrics,
        ),
        "plateaus": plateaus,
        "fatigue_pattern": (
            detect_longitudinal_fatigue_pattern(
                ordered
            )
        ),
        "personal_bests": (
            build_personal_best_map(
                ordered,
                metric_names=metrics,
            )
        ),
        "engine_version": "1.0.0",
        "limitations": [
            "Longitudinal comparisons are only meaningful when recording conditions and event protocols are reasonably consistent.",
            "Fatigue patterns are screening signals, not medical conclusions.",
            "Trend interpretation requires at least three comparable sessions.",
        ],
    }
