from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.back_side_models import (
    BackSideFrame,
    BackSideMetrics,
)


SUPPORTED_PHASES = {
    "drive",
    "transition",
    "maximum_velocity",
}


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def _body_height_proxy(
    frame: BackSideFrame,
) -> float:
    y_values = [
        frame.shoulder_y,
        frame.hip_y,
        frame.knee_y,
        frame.ankle_y,
        frame.heel_y,
        frame.toe_y,
        frame.com_y,
    ]

    return max(
        max(y_values) - min(y_values),
        1e-6,
    )


def _trailing_foot_distance_percent(
    frame: BackSideFrame,
) -> float:
    body_height = _body_height_proxy(
        frame
    )

    # Positive means the foot is behind the COM for a left-to-right sprint.
    return max(
        0.0,
        frame.com_x - frame.toe_x,
    ) / body_height * 100.0


def _heel_speed(
    frame: BackSideFrame,
) -> float | None:
    if (
        frame.heel_velocity_x is None
        or frame.heel_velocity_y is None
    ):
        return None

    return (
        frame.heel_velocity_x**2
        + frame.heel_velocity_y**2
    ) ** 0.5


def _rear_swing_velocity(
    frame: BackSideFrame,
) -> float | None:
    if frame.heel_velocity_x is None:
        return None

    # For left-to-right movement, forward recovery is positive x.
    return max(
        0.0,
        frame.heel_velocity_x,
    )


def _estimate_back_side_duration_ms(
    frames: list[BackSideFrame],
) -> float | None:
    trailing = [
        frame
        for frame in frames
        if frame.toe_x < frame.com_x
    ]

    if len(trailing) < 2:
        return None

    return float(
        trailing[-1].timestamp_ms
        - trailing[0].timestamp_ms
    )


def _push_off_completion(
    frames: list[BackSideFrame],
) -> float | None:
    toe_off_candidates = [
        frame
        for frame in frames
        if frame.toe_off_probability is not None
    ]

    if not toe_off_candidates:
        return None

    strongest = max(
        toe_off_candidates,
        key=lambda frame: (
            frame.toe_off_probability
            or 0.0
        ),
    )

    components: list[float] = []

    if strongest.hip_angle_deg is not None:
        # Larger extension receives a better score.
        components.append(
            _clamp(
                (
                    strongest.hip_angle_deg
                    - 120.0
                )
                / 50.0
            )
        )

    if strongest.knee_angle_deg is not None:
        components.append(
            _clamp(
                (
                    strongest.knee_angle_deg
                    - 130.0
                )
                / 45.0
            )
        )

    if strongest.ankle_velocity_x is not None:
        components.append(
            _clamp(
                abs(
                    strongest.ankle_velocity_x
                )
                / 2.5
            )
        )

    components.append(
        _clamp(
            strongest.toe_off_probability
            or 0.0
        )
    )

    if not components:
        return None

    return round(
        mean(components)
        * 100.0,
        2,
    )


def _score_metrics(
    *,
    hip_extension_deg: float | None,
    trailing_distance_percent: float | None,
    heel_recovery_speed: float | None,
    back_side_duration_ms: float | None,
    push_off_score: float | None,
    rear_swing_velocity: float | None,
    confidence: float,
) -> float | None:
    components: list[float] = []

    if hip_extension_deg is not None:
        components.append(
            _clamp(
                (
                    hip_extension_deg
                    - 120.0
                )
                / 50.0
            )
        )

    if trailing_distance_percent is not None:
        components.append(
            _clamp(
                1.0
                - trailing_distance_percent
                / 45.0
            )
        )

    if heel_recovery_speed is not None:
        components.append(
            _clamp(
                heel_recovery_speed
                / 2.5
            )
        )

    if back_side_duration_ms is not None:
        components.append(
            _clamp(
                1.0
                - back_side_duration_ms
                / 350.0
            )
        )

    if push_off_score is not None:
        components.append(
            _clamp(
                push_off_score
                / 100.0
            )
        )

    if rear_swing_velocity is not None:
        components.append(
            _clamp(
                rear_swing_velocity
                / 2.5
            )
        )

    if not components:
        return None

    return round(
        mean(components)
        * _clamp(confidence)
        * 100.0,
        2,
    )


def analyze_back_side_mechanics(
    frames: list[BackSideFrame],
    *,
    side: str,
    phase: str,
) -> dict[str, Any]:
    if phase not in SUPPORTED_PHASES:
        return {
            "status": "unsupported_phase",
            "metrics": None,
        }

    selected = sorted(
        [
            frame
            for frame in frames
            if frame.side == side
            and frame.phase == phase
        ],
        key=lambda frame: (
            frame.timestamp_ms
        ),
    )

    if len(selected) < 3:
        return {
            "status": "insufficient_data",
            "metrics": None,
        }

    hip_extension_values = [
        frame.hip_angle_deg
        for frame in selected
        if frame.hip_angle_deg is not None
    ]

    trailing_distances = [
        _trailing_foot_distance_percent(
            frame
        )
        for frame in selected
    ]

    heel_speeds = [
        speed
        for speed in (
            _heel_speed(frame)
            for frame in selected
        )
        if speed is not None
    ]

    rear_swing_velocities = [
        velocity
        for velocity in (
            _rear_swing_velocity(
                frame
            )
            for frame in selected
        )
        if velocity is not None
    ]

    confidence = mean(
        _clamp(
            frame.confidence
        )
        for frame in selected
    )

    maximum_hip_extension = (
        max(
            hip_extension_values
        )
        if hip_extension_values
        else None
    )

    maximum_trailing_distance = max(
        trailing_distances
    )

    peak_heel_recovery_speed = (
        max(
            heel_speeds
        )
        if heel_speeds
        else None
    )

    duration_ms = (
        _estimate_back_side_duration_ms(
            selected
        )
    )

    push_off_score = _push_off_completion(
        selected
    )

    rear_swing_velocity = (
        max(
            rear_swing_velocities
        )
        if rear_swing_velocities
        else None
    )

    if (
        maximum_trailing_distance > 30.0
        or (
            duration_ms is not None
            and duration_ms > 260.0
        )
    ):
        risk = "high"

    elif (
        maximum_trailing_distance > 18.0
        or (
            duration_ms is not None
            and duration_ms > 180.0
        )
    ):
        risk = "moderate"

    else:
        risk = "low"

    score = _score_metrics(
        hip_extension_deg=(
            maximum_hip_extension
        ),
        trailing_distance_percent=(
            maximum_trailing_distance
        ),
        heel_recovery_speed=(
            peak_heel_recovery_speed
        ),
        back_side_duration_ms=(
            duration_ms
        ),
        push_off_score=(
            push_off_score
        ),
        rear_swing_velocity=(
            rear_swing_velocity
        ),
        confidence=confidence,
    )

    metrics = BackSideMetrics(
        side=side,
        phase=phase,
        frames_used=len(
            selected
        ),
        maximum_hip_extension_deg=(
            round(
                maximum_hip_extension,
                2,
            )
            if maximum_hip_extension
            is not None
            else None
        ),
        maximum_trailing_foot_distance_body_height_percent=round(
            maximum_trailing_distance,
            2,
        ),
        peak_heel_recovery_speed_normalized=(
            round(
                peak_heel_recovery_speed,
                4,
            )
            if peak_heel_recovery_speed
            is not None
            else None
        ),
        average_back_side_duration_ms=(
            round(
                duration_ms,
                2,
            )
            if duration_ms
            is not None
            else None
        ),
        push_off_completion_score=(
            push_off_score
        ),
        rear_swing_velocity_normalized=(
            round(
                rear_swing_velocity,
                4,
            )
            if rear_swing_velocity
            is not None
            else None
        ),
        back_side_risk=risk,
        score=score,
        confidence=round(
            confidence
            * 100.0,
            2,
        ),
    )

    return {
        "status": "experimental",
        "metrics": (
            metrics.to_dict()
        ),
        "limitations": [
            "All distances and velocities are normalized image-space values.",
            "Hip extension is a projected 2D image-plane measurement.",
            "Push-off completion is inferred and not force-plate measured.",
            "Thresholds require validation against manually labelled sprint footage.",
        ],
        "engine_version": "0.1.0",
    }
