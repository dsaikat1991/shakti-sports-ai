from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.phase_models import (
    SprintPhaseFrame,
    SprintPhaseSegment,
    SprintSignalFrame,
)
from app.services.sprint.velocity_profile import (
    build_velocity_profile,
)


def _torso_upright_score(
    angle: float | None,
) -> float:
    if angle is None:
        return 0.5

    # Assumes 0° is horizontal and 90° is upright.
    return max(
        0.0,
        min(
            1.0,
            (float(angle) - 20.0) / 70.0,
        ),
    )


def _phase_for_frame(
    *,
    index: int,
    total_frames: int,
    velocity_n: float,
    acceleration_n: float,
    upright_score: float,
    peak_velocity_index: int,
) -> tuple[str, float, dict[str, float]]:
    progress = (
        index / max(total_frames - 1, 1)
    )

    evidence = {
        "progress": round(progress, 4),
        "velocity": round(velocity_n, 4),
        "acceleration": round(acceleration_n, 4),
        "upright": round(upright_score, 4),
    }

    if index == 0 and velocity_n < 0.08:
        return "standing", 0.90, evidence

    if progress <= 0.08 and acceleration_n >= 0.55:
        return "start", 0.82, evidence

    if (
        acceleration_n >= 0.45
        and velocity_n < 0.72
        and upright_score < 0.72
    ):
        confidence = (
            acceleration_n * 0.45
            + (1.0 - velocity_n) * 0.25
            + (1.0 - upright_score) * 0.30
        )
        return "drive", confidence, evidence

    if (
        velocity_n >= 0.55
        and acceleration_n < 0.55
        and upright_score < 0.90
        and index <= peak_velocity_index
    ):
        confidence = (
            velocity_n * 0.40
            + (1.0 - acceleration_n) * 0.30
            + upright_score * 0.30
        )
        return "transition", confidence, evidence

    if (
        velocity_n >= 0.82
        and index <= peak_velocity_index + 2
    ):
        confidence = (
            velocity_n * 0.70
            + upright_score * 0.30
        )
        return "maximum_velocity", confidence, evidence

    if (
        index > peak_velocity_index
        and velocity_n < 0.78
    ):
        confidence = (
            (1.0 - velocity_n) * 0.65
            + progress * 0.35
        )
        return "deceleration", confidence, evidence

    if index > peak_velocity_index:
        return "maximum_velocity", 0.68, evidence

    return "transition", 0.60, evidence


def _smooth_phase_labels(
    labels: list[str],
) -> list[str]:
    if len(labels) < 3:
        return labels

    result = labels.copy()

    for index in range(1, len(labels) - 1):
        if (
            labels[index - 1]
            == labels[index + 1]
            and labels[index]
            != labels[index - 1]
        ):
            result[index] = labels[index - 1]

    return result


def _segments_from_frames(
    phase_frames: list[SprintPhaseFrame],
) -> list[SprintPhaseSegment]:
    if not phase_frames:
        return []

    segments: list[SprintPhaseSegment] = []

    start = 0

    for index in range(1, len(phase_frames) + 1):
        boundary = (
            index == len(phase_frames)
            or phase_frames[index].phase
            != phase_frames[start].phase
        )

        if not boundary:
            continue

        window = phase_frames[start:index]

        segments.append(
            SprintPhaseSegment(
                phase=phase_frames[start].phase,
                start_frame=window[0].frame_index,
                end_frame=window[-1].frame_index,
                start_ms=window[0].timestamp_ms,
                end_ms=window[-1].timestamp_ms,
                duration_ms=(
                    window[-1].timestamp_ms
                    - window[0].timestamp_ms
                ),
                average_confidence=round(
                    mean(
                        frame.confidence
                        for frame in window
                    )
                    * 100.0,
                    2,
                ),
            )
        )

        start = index

    return segments


def detect_sprint_phases_v2(
    frames: list[SprintSignalFrame],
) -> dict[str, Any]:
    if len(frames) < 8:
        return {
            "status": "insufficient_data",
            "phase_frames": [],
            "segments": [],
        }

    ordered = sorted(
        frames,
        key=lambda frame: frame.timestamp_ms,
    )

    profile = build_velocity_profile(
        ordered
    )

    if profile["status"] != "completed":
        return {
            "status": "insufficient_data",
            "phase_frames": [],
            "segments": [],
        }

    raw: list[
        tuple[str, float, dict[str, float]]
    ] = []

    for index, frame in enumerate(ordered):
        raw.append(
            _phase_for_frame(
                index=index,
                total_frames=len(ordered),
                velocity_n=profile[
                    "normalized_velocity"
                ][index],
                acceleration_n=profile[
                    "normalized_positive_acceleration"
                ][index],
                upright_score=_torso_upright_score(
                    frame.torso_angle_deg
                ),
                peak_velocity_index=profile[
                    "peak_velocity_index"
                ],
            )
        )

    labels = _smooth_phase_labels(
        [
            item[0]
            for item in raw
        ]
    )

    phase_frames = [
        SprintPhaseFrame(
            frame_index=frame.frame_index,
            timestamp_ms=frame.timestamp_ms,
            phase=labels[index],
            confidence=round(
                max(
                    0.0,
                    min(
                        1.0,
                        raw[index][1]
                        * frame.confidence,
                    ),
                ),
                4,
            ),
            evidence=raw[index][2],
        )
        for index, frame in enumerate(ordered)
    ]

    segments = _segments_from_frames(
        phase_frames
    )

    return {
        "status": "experimental",
        "phase_frames": [
            frame.to_dict()
            for frame in phase_frames
        ],
        "segments": [
            segment.to_dict()
            for segment in segments
        ],
        "velocity_profile": profile,
        "overall_confidence": round(
            mean(
                frame.confidence
                for frame in phase_frames
            )
            * 100.0,
            2,
        ),
        "limitations": [
            "Start and standing labels are provisional without block or gun detection.",
            "Phase boundaries require validation against manually labelled sprint clips.",
            "The detector is intended for side-view sprint footage.",
        ],
    }
