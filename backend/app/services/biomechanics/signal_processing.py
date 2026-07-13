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


def remove_outliers_local(
    samples: list[AngleSample],
    *,
    window: int = 5,
    threshold: float = 4.0,
) -> list[AngleSample]:
    """
    Hampel-style local outlier removal.

    A joint-angle series from running is expected to swing widely and
    periodically (e.g. a knee cycling between near-extension and deep
    flexion every stride). ``remove_outliers_mad`` compares every sample
    against the whole clip's median, so the numerically rarer flexion
    peaks - the exact values cadence/cycle detection needs - get flagged
    as outliers and removed. Comparing each sample only to its immediate
    temporal neighbors instead preserves a genuine multi-frame swing
    (its neighbors move together with it) while still catching an
    isolated single-frame tracking glitch (which looks inconsistent with
    both neighbors).
    """
    if len(samples) < window:
        return samples.copy()

    values = np.array(
        [sample.angle_degrees for sample in samples],
        dtype=float,
    )
    radius = window // 2
    kept: list[AngleSample] = []

    for index, sample in enumerate(samples):
        start = max(0, index - radius)
        end = min(len(samples), index + radius + 1)
        neighbours = np.delete(values[start:end], index - start)

        if neighbours.size == 0:
            kept.append(sample)
            continue

        local_median = float(np.median(neighbours))
        local_mad = float(np.median(np.abs(neighbours - local_median)))

        if local_mad == 0.0:
            kept.append(sample)
            continue

        robust_z = 0.6745 * abs(values[index] - local_median) / local_mad
        if robust_z <= threshold:
            kept.append(sample)

    return kept


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


def prepare_angle_segments(
    frame_metrics: list[FrameMetrics],
    angle_name: str,
) -> list[list[AngleSample]]:
    """
    Prepare one smoothed, outlier-cleaned angle series per contiguous
    time segment.

    Earlier versions kept only the single longest contiguous segment and
    discarded the rest, which silently threw away real motion data
    whenever a later, longer stretch of a clip happened to exist -
    including, in practice, the highest-amplitude flexion/extension
    cycles when RTMPose confidence dips during fast movement fragment
    the series into several shorter runs. Callers that must not compare
    samples across a timing gap (smoothing windows, local-extrema
    detection) should operate on each segment independently; callers
    that only need overall coverage/summary statistics can flatten the
    result.

    Outlier removal uses the local (Hampel-style) filter rather than the
    whole-clip MAD filter, since a global filter treats genuine flexion
    peaks - a numeric minority of any running cycle - as outliers.
    """
    raw = extract_angle_series(frame_metrics, angle_name)
    cleaned = remove_outliers_local(raw)
    segments = split_contiguous_segments(cleaned)

    return [
        smooth_angle_series(segment, window_size=5)
        for segment in segments
        if segment
    ]


def prepare_angle_series(
    frame_metrics: list[FrameMetrics],
    angle_name: str,
) -> list[AngleSample]:
    """Flattened view of all prepared segments, ordered by frame index.

    Suitable for summary statistics (coverage, mean, percentiles) that
    don't depend on temporal adjacency between samples.
    """
    segments = prepare_angle_segments(frame_metrics, angle_name)
    flattened: list[AngleSample] = [
        sample
        for segment in segments
        for sample in segment
    ]
    flattened.sort(key=lambda sample: sample.frame_index)

    return flattened


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
