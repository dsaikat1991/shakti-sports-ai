from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics


@dataclass(slots=True, frozen=True)
class AngleSample:
    frame_index: int
    timestamp_ms: int
    angle_degrees: float


def extract_angle_series(
    frame_metrics: Iterable[FrameMetrics],
    angle_name: str,
) -> list[AngleSample]:
    samples: list[AngleSample] = []

    for frame in frame_metrics:
        angle = frame.joint_angles.get(angle_name)
        if angle is None:
            continue

        samples.append(
            AngleSample(
                frame_index=frame.frame_index,
                timestamp_ms=frame.timestamp_ms,
                angle_degrees=float(angle),
            )
        )

    return samples


def split_contiguous_segments(
    samples: list[AngleSample],
    *,
    maximum_gap_multiplier: float = 2.5,
) -> list[list[AngleSample]]:
    if not samples:
        return []

    if len(samples) == 1:
        return [samples.copy()]

    intervals = [
        samples[index].timestamp_ms - samples[index - 1].timestamp_ms
        for index in range(1, len(samples))
        if samples[index].timestamp_ms > samples[index - 1].timestamp_ms
    ]

    expected_interval = float(median(intervals)) if intervals else 0.0
    maximum_gap = (
        expected_interval * maximum_gap_multiplier
        if expected_interval > 0
        else float("inf")
    )

    segments: list[list[AngleSample]] = []
    current_segment: list[AngleSample] = [samples[0]]

    for index in range(1, len(samples)):
        previous = samples[index - 1]
        current = samples[index]
        gap = current.timestamp_ms - previous.timestamp_ms

        if gap <= maximum_gap:
            current_segment.append(current)
        else:
            segments.append(current_segment)
            current_segment = [current]

    segments.append(current_segment)
    return segments


def select_longest_segment(
    samples: list[AngleSample],
) -> list[AngleSample]:
    segments = split_contiguous_segments(samples)

    if not segments:
        return []

    return max(
        segments,
        key=lambda segment: (
            len(segment),
            segment[-1].timestamp_ms - segment[0].timestamp_ms,
        ),
    )


def remove_outliers_mad(
    samples: list[AngleSample],
    *,
    threshold: float = 3.5,
) -> list[AngleSample]:
    if len(samples) < 5:
        return samples.copy()

    values = np.array(
        [sample.angle_degrees for sample in samples],
        dtype=float,
    )

    center = float(np.median(values))
    absolute_deviations = np.abs(values - center)
    mad = float(np.median(absolute_deviations))

    if mad == 0.0:
        return samples.copy()

    robust_z_scores = 0.6745 * (values - center) / mad

    return [
        sample
        for sample, robust_z in zip(samples, robust_z_scores)
        if abs(float(robust_z)) <= threshold
    ]


def smooth_angle_series(
    samples: list[AngleSample],
    *,
    window_size: int = 5,
) -> list[AngleSample]:
    if window_size <= 1 or len(samples) < 3:
        return samples.copy()

    if window_size % 2 == 0:
        window_size += 1

    radius = window_size // 2
    smoothed: list[AngleSample] = []

    for index, sample in enumerate(samples):
        start = max(0, index - radius)
        end = min(len(samples), index + radius + 1)
        window = samples[start:end]

        average_angle = float(
            np.mean([item.angle_degrees for item in window])
        )

        smoothed.append(
            AngleSample(
                frame_index=sample.frame_index,
                timestamp_ms=sample.timestamp_ms,
                angle_degrees=average_angle,
            )
        )

    return smoothed


def prepare_angle_series(
    frame_metrics: list[FrameMetrics],
    angle_name: str,
) -> list[AngleSample]:
    raw = extract_angle_series(frame_metrics, angle_name)
    longest = select_longest_segment(raw)
    filtered = remove_outliers_mad(longest)

    return smooth_angle_series(
        filtered,
        window_size=5,
    )


def robust_angle_summary(
    samples: list[AngleSample],
) -> dict[str, float | int | None]:
    if not samples:
        return {
            "frames_with_value": 0,
            "minimum_degrees": None,
            "maximum_degrees": None,
            "average_degrees": None,
            "range_degrees": None,
            "p05_degrees": None,
            "p95_degrees": None,
        }

    values = np.array(
        [sample.angle_degrees for sample in samples],
        dtype=float,
    )

    p05 = float(np.percentile(values, 5))
    p95 = float(np.percentile(values, 95))

    return {
        "frames_with_value": len(samples),
        "minimum_degrees": round(float(np.min(values)), 2),
        "maximum_degrees": round(float(np.max(values)), 2),
        "average_degrees": round(float(np.mean(values)), 2),
        "range_degrees": round(p95 - p05, 2),
        "p05_degrees": round(p05, 2),
        "p95_degrees": round(p95, 2),
    }
