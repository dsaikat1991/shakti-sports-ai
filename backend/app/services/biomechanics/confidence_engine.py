from __future__ import annotations

from typing import Any


def combine_confidences(
    values: list[float],
    *,
    minimum_required: int = 1,
) -> float | None:
    valid = [
        max(0.0, min(1.0, float(value)))
        for value in values
        if value is not None
    ]

    if len(valid) < minimum_required:
        return None

    product = 1.0

    for value in valid:
        product *= max(value, 1e-6)

    return product ** (1.0 / len(valid))


def metric_confidence(
    *,
    landmark_confidence: float | None,
    trajectory_continuity: float | None,
    camera_confidence: float | None,
    event_confidence: float | None = None,
) -> dict[str, Any]:
    components = {
        "landmark_confidence": (
            landmark_confidence
        ),
        "trajectory_continuity": (
            trajectory_continuity
        ),
        "camera_confidence": (
            camera_confidence
        ),
        "event_confidence": event_confidence,
    }

    combined = combine_confidences(
        [
            value
            for value in components.values()
            if value is not None
        ],
        minimum_required=2,
    )

    if combined is None:
        return {
            "score": None,
            "rating": "insufficient_data",
            "components": components,
        }

    if combined >= 0.90:
        rating = "very_high"
    elif combined >= 0.80:
        rating = "high"
    elif combined >= 0.65:
        rating = "moderate"
    elif combined >= 0.50:
        rating = "low"
    else:
        rating = "very_low"

    return {
        "score": round(
            combined * 100.0,
            2,
        ),
        "rating": rating,
        "components": components,
    }


def trajectory_continuity_score(
    *,
    measured_points: int,
    predicted_points: int,
    missing_points: int,
) -> float:
    total = (
        measured_points
        + predicted_points
        + missing_points
    )

    if total <= 0:
        return 0.0

    measured_weight = measured_points * 1.0
    predicted_weight = predicted_points * 0.6

    return max(
        0.0,
        min(
            1.0,
            (
                measured_weight
                + predicted_weight
            )
            / total,
        ),
    )
