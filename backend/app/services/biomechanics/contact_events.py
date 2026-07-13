from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics


LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32

MIN_CONFIDENCE = 0.50


@dataclass(slots=True, frozen=True)
class FootSample:
    side: str
    frame_index: int
    timestamp_ms: int
    normalized_y: float


@dataclass(slots=True, frozen=True)
class ContactEvent:
    side: str
    contact_start_ms: int
    contact_end_ms: int
    contact_time_ms: int
    peak_frame_index: int
    peak_timestamp_ms: int
    confidence: float


def _value(
    landmark: Any,
    name: str,
    default: float = 0.0,
) -> float:
    if isinstance(landmark, dict):
        return float(landmark.get(name, default))

    return float(getattr(landmark, name, default))


def _is_reliable(landmark: Any) -> bool:
    return (
        _value(landmark, "visibility") >= MIN_CONFIDENCE
        and _value(landmark, "presence") >= MIN_CONFIDENCE
        and 0.0 <= _value(landmark, "x") <= 1.0
        and 0.0 <= _value(landmark, "y") <= 1.0
    )


def _foot_height(
    landmarks: tuple[Any, ...],
    indices: tuple[int, int, int],
) -> float | None:
    points = [
        landmarks[index]
        for index in indices
        if index < len(landmarks)
        and _is_reliable(landmarks[index])
    ]

    if len(points) < 2:
        return None

    return float(
        np.mean(
            [_value(point, "y") for point in points]
        )
    )


def extract_foot_series(
    frame_metrics: list[FrameMetrics],
) -> dict[str, list[FootSample]]:
    result: dict[str, list[FootSample]] = {
        "left": [],
        "right": [],
    }

    for frame in frame_metrics:
        left_y = _foot_height(
            frame.landmarks,
            (
                LEFT_ANKLE,
                LEFT_HEEL,
                LEFT_FOOT_INDEX,
            ),
        )

        right_y = _foot_height(
            frame.landmarks,
            (
                RIGHT_ANKLE,
                RIGHT_HEEL,
                RIGHT_FOOT_INDEX,
            ),
        )

        if left_y is not None:
            result["left"].append(
                FootSample(
                    side="left",
                    frame_index=frame.frame_index,
                    timestamp_ms=frame.timestamp_ms,
                    normalized_y=left_y,
                )
            )

        if right_y is not None:
            result["right"].append(
                FootSample(
                    side="right",
                    frame_index=frame.frame_index,
                    timestamp_ms=frame.timestamp_ms,
                    normalized_y=right_y,
                )
            )

    return result


def _smooth_series(
    samples: list[FootSample],
    window_size: int = 5,
) -> list[FootSample]:
    if len(samples) < 3:
        return samples.copy()

    if window_size % 2 == 0:
        window_size += 1

    radius = window_size // 2
    smoothed: list[FootSample] = []

    for index, sample in enumerate(samples):
        start = max(0, index - radius)
        end = min(len(samples), index + radius + 1)
        window = samples[start:end]

        smoothed.append(
            FootSample(
                side=sample.side,
                frame_index=sample.frame_index,
                timestamp_ms=sample.timestamp_ms,
                normalized_y=float(
                    np.mean(
                        [item.normalized_y for item in window]
                    )
                ),
            )
        )

    return smoothed


def _expected_interval_ms(
    samples: list[FootSample],
) -> float:
    intervals = [
        samples[index].timestamp_ms
        - samples[index - 1].timestamp_ms
        for index in range(1, len(samples))
        if (
            samples[index].timestamp_ms
            > samples[index - 1].timestamp_ms
        )
    ]

    return float(median(intervals)) if intervals else 0.0


def _detect_side_contacts(
    samples: list[FootSample],
    *,
    minimum_prominence: float = 0.006,
) -> list[ContactEvent]:
    """
    Detect provisional contact windows from local maxima in image-space
    foot height.

    In normalized image coordinates, larger y usually means the foot is
    closer to the ground plane. This is only a proxy and must be calibrated
    against labelled sprint video.
    """

    smoothed = _smooth_series(samples)

    if len(smoothed) < 5:
        return []

    interval_ms = _expected_interval_ms(smoothed)

    if interval_ms <= 0:
        return []

    values = np.array(
        [sample.normalized_y for sample in smoothed],
        dtype=float,
    )

    upper_quartile = float(
        np.percentile(values, 75)
    )

    events: list[ContactEvent] = []
    last_peak_time = -10_000

    for index in range(2, len(smoothed) - 2):
        current = smoothed[index]
        current_y = current.normalized_y

        local_window = smoothed[index - 2:index + 3]
        local_minimum = min(
            item.normalized_y
            for item in local_window
        )

        is_local_maximum = (
            current_y >= smoothed[index - 1].normalized_y
            and current_y > smoothed[index + 1].normalized_y
        )

        prominence = current_y - local_minimum

        if (
            not is_local_maximum
            or current_y < upper_quartile
            or prominence < minimum_prominence
        ):
            continue

        # Avoid duplicate peaks from the same stance window.
        if current.timestamp_ms - last_peak_time < 180:
            continue

        tolerance = max(
            0.004,
            prominence * 0.40,
        )

        start_index = index
        end_index = index

        while (
            start_index > 0
            and current_y
            - smoothed[start_index - 1].normalized_y
            <= tolerance
        ):
            start_index -= 1

        while (
            end_index < len(smoothed) - 1
            and current_y
            - smoothed[end_index + 1].normalized_y
            <= tolerance
        ):
            end_index += 1

        start_ms = smoothed[start_index].timestamp_ms
        end_ms = smoothed[end_index].timestamp_ms

        # Add one sampling interval so a single-frame contact does not
        # become zero milliseconds.
        contact_time_ms = int(
            round(end_ms - start_ms + interval_ms)
        )

        if not 40 <= contact_time_ms <= 400:
            continue

        confidence = min(
            100.0,
            45.0
            + prominence * 2500.0
            + min(len(local_window), 5) * 3.0,
        )

        events.append(
            ContactEvent(
                side=current.side,
                contact_start_ms=start_ms,
                contact_end_ms=end_ms,
                contact_time_ms=contact_time_ms,
                peak_frame_index=current.frame_index,
                peak_timestamp_ms=current.timestamp_ms,
                confidence=round(confidence, 2),
            )
        )

        last_peak_time = current.timestamp_ms

    return events


def detect_contact_events(
    frame_metrics: list[FrameMetrics],
) -> dict[str, list[dict[str, int | float | str]]]:
    foot_series = extract_foot_series(
        frame_metrics
    )

    result: dict[
        str,
        list[dict[str, int | float | str]],
    ] = {
        "left": [],
        "right": [],
    }

    for side in ("left", "right"):
        events = _detect_side_contacts(
            foot_series[side]
        )

        result[side] = [
            {
                "side": event.side,
                "contact_start_ms": event.contact_start_ms,
                "contact_end_ms": event.contact_end_ms,
                "contact_time_ms": event.contact_time_ms,
                "peak_frame_index": event.peak_frame_index,
                "peak_timestamp_ms": event.peak_timestamp_ms,
                "confidence": event.confidence,
                "method": "foot_y_local_maximum_proxy",
            }
            for event in events
        ]

    return result


def summarize_contact_times(
    contact_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "status": "experimental",
        "left": {
            "events": 0,
            "average_contact_time_ms": None,
            "median_contact_time_ms": None,
        },
        "right": {
            "events": 0,
            "average_contact_time_ms": None,
            "median_contact_time_ms": None,
        },
        "overall": {
            "events": 0,
            "average_contact_time_ms": None,
            "median_contact_time_ms": None,
        },
        "warning": (
            "Ground-contact timing is estimated from image-space foot "
            "trajectory and is not yet validated against force plates."
        ),
    }

    all_times: list[float] = []

    for side in ("left", "right"):
        times = [
            float(event["contact_time_ms"])
            for event in contact_events.get(side, [])
            if isinstance(
                event.get("contact_time_ms"),
                (int, float),
            )
        ]

        all_times.extend(times)

        if times:
            summary[side] = {
                "events": len(times),
                "average_contact_time_ms": round(
                    float(np.mean(times)),
                    2,
                ),
                "median_contact_time_ms": round(
                    float(np.median(times)),
                    2,
                ),
            }

    if all_times:
        summary["overall"] = {
            "events": len(all_times),
            "average_contact_time_ms": round(
                float(np.mean(all_times)),
                2,
            ),
            "median_contact_time_ms": round(
                float(np.median(all_times)),
                2,
            ),
        }
    else:
        summary["status"] = "insufficient_data"

    return summary
