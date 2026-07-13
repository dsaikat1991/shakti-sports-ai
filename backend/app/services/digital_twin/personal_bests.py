from __future__ import annotations

from typing import Any

from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
    PersonalBest,
)


LOWER_IS_BETTER = {
    "ground_contact_ms",
    "vertical_oscillation_percent",
    "cadence_cv_percent",
    "contact_cv_percent",
    "flight_cv_percent",
    "back_side_duration_ms",
    "trailing_distance_percent",
}


def find_personal_best(
    snapshots: list[AthleteMetricSnapshot],
    *,
    metric_name: str,
    lower_is_better: bool | None = None,
) -> dict[str, Any]:
    usable = [
        snapshot
        for snapshot in snapshots
        if metric_name
        in snapshot.metrics
    ]

    if not usable:
        return {
            "status": "insufficient_data",
            "personal_best": None,
        }

    if lower_is_better is None:
        lower_is_better = (
            metric_name
            in LOWER_IS_BETTER
        )

    best_snapshot = (
        min(
            usable,
            key=lambda snapshot: (
                snapshot.metrics[
                    metric_name
                ]
            ),
        )
        if lower_is_better
        else max(
            usable,
            key=lambda snapshot: (
                snapshot.metrics[
                    metric_name
                ]
            ),
        )
    )

    personal_best = PersonalBest(
        metric_name=metric_name,
        value=float(
            best_snapshot.metrics[
                metric_name
            ]
        ),
        performance_id=(
            best_snapshot.performance_id
        ),
        recorded_at=(
            best_snapshot.recorded_at
        ),
        objective=(
            "minimum"
            if lower_is_better
            else "maximum"
        ),
    )

    return {
        "status": "completed",
        "personal_best": (
            personal_best.to_dict()
        ),
    }


def build_personal_best_map(
    snapshots: list[AthleteMetricSnapshot],
    *,
    metric_names: list[str],
) -> dict[str, Any]:
    return {
        metric_name: find_personal_best(
            snapshots,
            metric_name=metric_name,
        )
        for metric_name in metric_names
    }
