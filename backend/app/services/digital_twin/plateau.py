from __future__ import annotations

from statistics import mean
from typing import Any

import numpy as np

from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
)


def detect_plateau(
    snapshots: list[AthleteMetricSnapshot],
    *,
    metric_name: str,
    recent_window: int = 4,
    maximum_relative_slope_percent: float = 0.75,
    maximum_cv_percent: float = 5.0,
) -> dict[str, Any]:
    usable = [
        snapshot
        for snapshot in sorted(
            snapshots,
            key=lambda item: item.recorded_at,
        )
        if metric_name in snapshot.metrics
    ]

    if len(usable) < recent_window:
        return {
            "status": "insufficient_data",
            "plateau": False,
        }

    recent = usable[
        -recent_window:
    ]

    values = [
        float(
            snapshot.metrics[
                metric_name
            ]
        )
        for snapshot in recent
    ]

    average = mean(values)

    slope = float(
        np.polyfit(
            np.arange(
                len(values),
                dtype=float,
            ),
            np.asarray(
                values,
                dtype=float,
            ),
            1,
        )[0]
    )

    relative_slope_percent = (
        abs(slope)
        / abs(average)
        * 100.0
        if abs(average) > 1e-9
        else 0.0
    )

    cv_percent = (
        float(
            np.std(
                values,
                ddof=0,
            )
            / abs(average)
            * 100.0
        )
        if abs(average) > 1e-9
        else 0.0
    )

    plateau = (
        relative_slope_percent
        <= maximum_relative_slope_percent
        and cv_percent
        <= maximum_cv_percent
    )

    return {
        "status": "completed",
        "plateau": plateau,
        "metric_name": metric_name,
        "recent_window": recent_window,
        "relative_slope_percent": round(
            relative_slope_percent,
            3,
        ),
        "coefficient_of_variation_percent": round(
            cv_percent,
            3,
        ),
        "message": (
            "Recent performance appears to have plateaued."
            if plateau
            else "No stable plateau was detected."
        ),
    }
