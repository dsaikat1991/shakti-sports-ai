from __future__ import annotations

from statistics import mean
from typing import Any

import numpy as np

from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
    MetricTrend,
)


LOWER_IS_BETTER_DEFAULTS = {
    "ground_contact_ms",
    "vertical_oscillation_percent",
    "cadence_cv_percent",
    "contact_cv_percent",
    "flight_cv_percent",
    "back_side_duration_ms",
    "trailing_distance_percent",
}


def _average_confidence(
    snapshots: list[AthleteMetricSnapshot],
    metric_name: str,
) -> float | None:
    values = [
        snapshot.confidences[
            metric_name
        ]
        for snapshot in snapshots
        if snapshot.confidences
        and metric_name
        in snapshot.confidences
    ]

    if not values:
        return None

    return round(
        mean(values)
        * 100.0,
        2,
    )


def analyze_metric_trend(
    snapshots: list[AthleteMetricSnapshot],
    *,
    metric_name: str,
    lower_is_better: bool | None = None,
    minimum_samples: int = 3,
) -> dict[str, Any]:
    usable = [
        snapshot
        for snapshot in sorted(
            snapshots,
            key=lambda item: item.recorded_at,
        )
        if metric_name in snapshot.metrics
    ]

    if len(usable) < minimum_samples:
        return {
            "status": "insufficient_data",
            "trend": None,
        }

    values = [
        float(
            snapshot.metrics[
                metric_name
            ]
        )
        for snapshot in usable
    ]

    first = values[0]
    latest = values[-1]
    absolute_change = latest - first

    percent_change = (
        absolute_change
        / abs(first)
        * 100.0
        if abs(first) > 1e-9
        else None
    )

    x = np.arange(
        len(values),
        dtype=float,
    )

    slope = float(
        np.polyfit(
            x,
            np.asarray(
                values,
                dtype=float,
            ),
            1,
        )[0]
    )

    average = mean(values)

    coefficient_of_variation = (
        float(
            np.std(
                values,
                ddof=0,
            )
            / abs(average)
            * 100.0
        )
        if abs(average) > 1e-9
        else None
    )

    if lower_is_better is None:
        lower_is_better = (
            metric_name
            in LOWER_IS_BETTER_DEFAULTS
        )

    practical_threshold = max(
        abs(average) * 0.005,
        1e-9,
    )

    if abs(slope) < practical_threshold:
        direction = "stable"
    else:
        improving = (
            slope < 0.0
            if lower_is_better
            else slope > 0.0
        )

        direction = (
            "improving"
            if improving
            else "regressing"
        )

    if (
        coefficient_of_variation
        is not None
        and coefficient_of_variation
        > 12.0
    ):
        direction = "high_variability"

    trend = MetricTrend(
        metric_name=metric_name,
        samples=len(values),
        first_value=round(
            first,
            6,
        ),
        latest_value=round(
            latest,
            6,
        ),
        absolute_change=round(
            absolute_change,
            6,
        ),
        percent_change=(
            round(
                percent_change,
                2,
            )
            if percent_change
            is not None
            else None
        ),
        slope_per_session=round(
            slope,
            6,
        ),
        coefficient_of_variation_percent=(
            round(
                coefficient_of_variation,
                2,
            )
            if coefficient_of_variation
            is not None
            else None
        ),
        direction=direction,
        confidence=_average_confidence(
            usable,
            metric_name,
        ),
    )

    return {
        "status": "completed",
        "trend": trend.to_dict(),
    }


def build_trend_map(
    snapshots: list[AthleteMetricSnapshot],
    *,
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    available_metrics = sorted(
        {
            metric_name
            for snapshot in snapshots
            for metric_name
            in snapshot.metrics
        }
    )

    target_metrics = (
        metrics
        if metrics is not None
        else available_metrics
    )

    return {
        metric_name: analyze_metric_trend(
            snapshots,
            metric_name=metric_name,
        )
        for metric_name in target_metrics
    }
