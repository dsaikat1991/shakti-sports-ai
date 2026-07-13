from __future__ import annotations

from typing import Any

from app.services.digital_twin_v2.models import (
    PersonalBaseline,
    TwinSession,
)
from app.services.digital_twin_v2.statistics import (
    confidence_percent,
    summary,
)


def build_personal_baselines(
    sessions: list[TwinSession],
    *,
    minimum_samples: int = 3,
    recent_window: int | None = None,
) -> dict[str, Any]:
    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )

    if recent_window is not None:
        ordered = ordered[
            -recent_window:
        ]

    feature_names = sorted(
        {
            feature_name
            for session in ordered
            for feature_name
            in session.features
        }
    )

    baselines: dict[str, Any] = {}

    for feature_name in feature_names:
        values = [
            session.features[
                feature_name
            ]
            for session in ordered
            if feature_name
            in session.features
        ]

        if len(values) < minimum_samples:
            continue

        stats = summary(values)

        confidence_values = [
            session.confidences[
                feature_name
            ]
            for session in ordered
            if session.confidences
            and feature_name
            in session.confidences
        ]

        baseline = PersonalBaseline(
            feature_name=feature_name,
            samples=stats["samples"],
            mean=round(
                stats["mean"],
                6,
            ),
            standard_deviation=round(
                stats[
                    "standard_deviation"
                ],
                6,
            ),
            minimum=round(
                stats["minimum"],
                6,
            ),
            maximum=round(
                stats["maximum"],
                6,
            ),
            median=round(
                stats["median"],
                6,
            ),
            confidence=confidence_percent(
                confidence_values
            ),
        )

        baselines[
            feature_name
        ] = baseline.to_dict()

    return {
        "status": (
            "completed"
            if baselines
            else "insufficient_data"
        ),
        "features": baselines,
        "sessions_used": len(
            ordered
        ),
        "engine_version": "1.0.0",
    }
