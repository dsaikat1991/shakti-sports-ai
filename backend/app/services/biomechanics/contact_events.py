from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.pose.landmark_usability import landmark_is_usable


LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32


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


def _is_reliable(landmark: Any, *, backend: str = "mediapipe") -> bool:
    return (
        landmark_is_usable(landmark, backend=backend)
        and 0.0 <= _value(landmark, "x") <= 1.0
        and 0.0 <= _value(landmark, "y") <= 1.0
    )


def _foot_height(
    landmarks: tuple[Any, ...],
    indices: tuple[int, int, int],
    *,
    backend: str,
) -> float | None:
    points = [
        landmarks[index]
        for index in indices
        if index < len(landmarks)
        and _is_reliable(landmarks[index], backend=backend)
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
        backend = getattr(frame, "backend", "mediapipe")

        left_y = _foot_height(
            frame.landmarks,
            (
                LEFT_ANKLE,
                LEFT_HEEL,
                LEFT_FOOT_INDEX,
            ),
            backend=backend,
        )

        right_y = _foot_height(
            frame.landmarks,
            (
                RIGHT_ANKLE,
                RIGHT_HEEL,
                RIGHT_FOOT_INDEX,
            ),
            backend=backend,
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

    CONFIRMED ISSUE (ground-truth checked against real footage, not just
    unit tests): for a low, close, corner-angle camera, a foot curled up
    behind the body during swing/recovery (heel near the glutes) can
    project to as large or larger a y-value than the same foot at true
    ground contact - the heel/toe, pulled up and back toward a low
    camera, gets foreshortened into appearing "low in frame". Visually
    confirmed on 3 independent samples spread across a real clip: what
    this function labels a ground-contact peak is consistently the
    swing-phase peak-knee-flexion moment instead (the same event
    detect_knee_cycle_events correctly identifies) - not a calibration
    error, a wrong signal for this camera geometry.

    Alternatives tried and NOT confirmed as reliable either (each showed
    partial promise in event count but failed close visual inspection):
    ankle/toe velocity local minima (also fires at the swing-apex
    momentary pause, not just true stance), peak-knee-extension timing
    (too sparse - only ~3 events on a 15s clip), centre-of-mass vertical
    oscillation (closer - its ~49 local maxima across the clip nearly
    matches the ~46 real steps measured independently via cadence - but
    quantified against 4 manually reviewed gait cycles in
    tests/fixtures/ground_truth_contact_labels.json, mean absolute
    timing error was ~120ms for both this detector and the centre-of-
    mass approach, against a real contact duration of only 60-150ms.
    That's not a small calibration offset - it's large enough to land
    in the wrong phase of the cycle.

    Do not trust contact_time_ms / ground_contact / flight_time /
    duty_factor for this camera framing until this is properly solved -
    likely needs a labelled dataset across multiple camera angles rather
    than another single-signal heuristic.
    """

    smoothed = _smooth_series(samples)

    if len(smoothed) < 5:
        return []

    interval_ms = _expected_interval_ms(smoothed)

    if interval_ms <= 0:
        return []

    # First pass: every strict turning point relative to its immediate
    # neighbours. A real ground-contact plateau can span several frames
    # (a foot dwelling near the ground for ~100ms is 5+ frames at
    # 50fps), so the peak's *location* is still reliably found this
    # way even though prominence needs a wider view (below).
    turning_points: list[tuple[str, int]] = []

    for index in range(1, len(smoothed) - 1):
        current_y = smoothed[index].normalized_y
        previous_y = smoothed[index - 1].normalized_y
        next_y = smoothed[index + 1].normalized_y

        if current_y >= previous_y and current_y > next_y:
            turning_points.append(("maximum", index))
        elif current_y <= previous_y and current_y < next_y:
            turning_points.append(("minimum", index))

    events: list[ContactEvent] = []
    last_peak_time = -10_000

    for position, (kind, index) in enumerate(turning_points):
        if kind != "maximum":
            continue

        current = smoothed[index]
        current_y = current.normalized_y

        # Prominence relative to the nearer of the two surrounding
        # minima (or the series' own edge when there isn't one), not a
        # fixed narrow window - a global top-quartile height gate was
        # removed for the same reason: it rejects genuine contacts
        # whenever normal stride-to-stride variation or camera
        # perspective drift puts their peak below the whole clip's top
        # 25%, even though they are still clearly local maxima.
        left_bound = (
            smoothed[turning_points[position - 1][1]].normalized_y
            if position > 0
            else smoothed[0].normalized_y
        )
        right_bound = (
            smoothed[turning_points[position + 1][1]].normalized_y
            if position < len(turning_points) - 1
            else smoothed[-1].normalized_y
        )
        prominence = current_y - max(left_bound, right_bound)

        if prominence < minimum_prominence:
            continue

        # Avoid duplicate peaks from the same stance window.
        if current.timestamp_ms - last_peak_time < 180:
            continue

        # The contact *window width* is sized off a narrow local
        # prominence (how sharply the signal falls away right around
        # the peak), not the wide-view prominence above. That wide-view
        # figure is the whole stride's swing amplitude, and scaling a
        # tolerance off it would swallow most of the stride into the
        # "contact" window instead of just the stance plateau.
        narrow_start = max(0, index - 2)
        narrow_end = min(len(smoothed), index + 3)
        local_minimum = min(
            item.normalized_y
            for item in smoothed[narrow_start:narrow_end]
        )
        local_prominence = current_y - local_minimum

        tolerance = max(
            0.004,
            local_prominence * 0.40,
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
            + min(end_index - start_index + 1, 5) * 3.0,
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
            "trajectory and is not yet validated against force plates. "
            "CONFIRMED against real footage: for low/close camera angles, "
            "this detector can fire on the swing-phase peak-flexion moment "
            "instead of true ground contact (foreshortening makes a "
            "curled-up recovery foot appear as low in frame as a planted "
            "one). Treat contact_time_ms, flight_time, and duty_factor as "
            "unreliable until this is properly fixed, not just uncalibrated."
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
