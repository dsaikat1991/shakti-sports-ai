from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.pose.landmark_usability import landmark_is_usable


LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28


LANDMARK_WEIGHTS: dict[int, float] = {
    LEFT_SHOULDER: 0.10,
    RIGHT_SHOULDER: 0.10,
    LEFT_ELBOW: 0.04,
    RIGHT_ELBOW: 0.04,
    LEFT_WRIST: 0.02,
    RIGHT_WRIST: 0.02,
    LEFT_HIP: 0.20,
    RIGHT_HIP: 0.20,
    LEFT_KNEE: 0.10,
    RIGHT_KNEE: 0.10,
    LEFT_ANKLE: 0.04,
    RIGHT_ANKLE: 0.04,
}


@dataclass(slots=True, frozen=True)
class CentreSample:
    frame_index: int
    timestamp_ms: int
    x: float
    y: float
    body_height_normalized: float | None


def _value(
    landmark: Any,
    name: str,
    default: float = 0.0,
) -> float:
    if isinstance(landmark, dict):
        return float(landmark.get(name, default))

    return float(getattr(landmark, name, default))


def _is_reliable(landmark: Any, *, backend: str = "mediapipe") -> bool:
    return (
        landmark_is_usable(landmark, backend=backend)
        and 0.0 <= _value(landmark, "x") <= 1.0
        and 0.0 <= _value(landmark, "y") <= 1.0
    )


def _estimate_body_height(
    frame: FrameMetrics,
) -> float | None:
    box = frame.bounding_box

    if not box:
        return None

    height = box.get("height")

    if not isinstance(height, (int, float)):
        return None

    if float(height) <= 0:
        return None

    return float(height)


def estimate_frame_centre(
    frame: FrameMetrics,
) -> CentreSample | None:
    weighted_x = 0.0
    weighted_y = 0.0
    total_weight = 0.0
    backend = getattr(frame, "backend", "mediapipe")

    for index, weight in LANDMARK_WEIGHTS.items():
        if index >= len(frame.landmarks):
            continue

        landmark = frame.landmarks[index]

        if not _is_reliable(landmark, backend=backend):
            continue

        weighted_x += _value(landmark, "x") * weight
        weighted_y += _value(landmark, "y") * weight
        total_weight += weight

    # Require most of the weighted body model to be present.
    if total_weight < 0.65:
        return None

    return CentreSample(
        frame_index=frame.frame_index,
        timestamp_ms=frame.timestamp_ms,
        x=weighted_x / total_weight,
        y=weighted_y / total_weight,
        body_height_normalized=_estimate_body_height(frame),
    )


def extract_centre_series(
    frame_metrics: list[FrameMetrics],
) -> list[CentreSample]:
    samples: list[CentreSample] = []

    for frame in frame_metrics:
        sample = estimate_frame_centre(frame)

        if sample is not None:
            samples.append(sample)

    return samples


def _smooth_values(
    values: list[float],
    window_size: int = 5,
) -> list[float]:
    if len(values) < 3 or window_size <= 1:
        return values.copy()

    if window_size % 2 == 0:
        window_size += 1

    radius = window_size // 2
    smoothed: list[float] = []

    for index in range(len(values)):
        start = max(0, index - radius)
        end = min(len(values), index + radius + 1)

        smoothed.append(
            float(np.mean(values[start:end]))
        )

    return smoothed


def analyze_centre_of_mass(
    frame_metrics: list[FrameMetrics],
) -> dict[str, Any]:
    """
    Analyze a pose-derived centre proxy.

    This is not a laboratory-grade whole-body centre of mass. It is a
    weighted landmark-centre proxy intended for relative motion analysis.
    """

    samples = extract_centre_series(frame_metrics)

    if len(samples) < 5:
        return {
            "status": "insufficient_data",
            "samples_used": len(samples),
            "coverage_percent": round(
                len(samples) / max(len(frame_metrics), 1) * 100,
                2,
            ),
            "horizontal_progression_normalized": None,
            "vertical_oscillation_normalized": None,
            "vertical_oscillation_body_height_percent": None,
            "path_smoothness_score": None,
        }

    x_values = _smooth_values(
        [sample.x for sample in samples]
    )
    y_values = _smooth_values(
        [sample.y for sample in samples]
    )

    horizontal_progression = (
        x_values[-1] - x_values[0]
    )

    p05_y = float(np.percentile(y_values, 5))
    p95_y = float(np.percentile(y_values, 95))
    vertical_oscillation = p95_y - p05_y

    body_heights = [
        sample.body_height_normalized
        for sample in samples
        if sample.body_height_normalized is not None
        and sample.body_height_normalized > 0
    ]

    average_body_height = (
        float(mean(body_heights))
        if body_heights
        else None
    )

    oscillation_body_height_percent = (
        vertical_oscillation
        / average_body_height
        * 100.0
        if average_body_height
        else None
    )

    path_steps = [
        (
            (x_values[index] - x_values[index - 1]) ** 2
            + (y_values[index] - y_values[index - 1]) ** 2
        ) ** 0.5
        for index in range(1, len(x_values))
    ]

    if len(path_steps) >= 2:
        path_variability = float(
            np.std(path_steps)
        )
        average_step = float(
            np.mean(path_steps)
        )

        coefficient = (
            path_variability / average_step
            if average_step > 0
            else 1.0
        )

        smoothness_score = max(
            0.0,
            min(
                100.0,
                100.0 - coefficient * 100.0,
            ),
        )
    else:
        smoothness_score = None

    return {
        "status": "experimental",
        "samples_used": len(samples),
        "coverage_percent": round(
            len(samples) / max(len(frame_metrics), 1) * 100,
            2,
        ),
        "horizontal_progression_normalized": round(
            horizontal_progression,
            5,
        ),
        "vertical_oscillation_normalized": round(
            vertical_oscillation,
            5,
        ),
        "vertical_oscillation_body_height_percent": (
            round(
                oscillation_body_height_percent,
                2,
            )
            if oscillation_body_height_percent is not None
            else None
        ),
        "path_smoothness_score": (
            round(smoothness_score, 2)
            if smoothness_score is not None
            else None
        ),
        "average_body_height_normalized": (
            round(average_body_height, 5)
            if average_body_height is not None
            else None
        ),
        "method": "weighted_pose_landmark_centre_proxy",
        "warning": (
            "This is a pose-derived centre proxy, not a laboratory-grade "
            "whole-body centre-of-mass measurement."
        ),
    }
