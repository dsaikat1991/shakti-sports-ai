from __future__ import annotations

from math import atan2, degrees
from statistics import mean
from typing import Any

from app.services.sprint.front_side_models import (
    FrontSideFrame,
    FrontSideMetrics,
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
            value,
        ),
    )


def _body_height_proxy(
    frame: FrontSideFrame,
) -> float:
    points_y = [
        frame.hip_y,
        frame.knee_y,
        frame.ankle_y,
        frame.foot_y,
        frame.com_y,
    ]

    height = max(points_y) - min(points_y)

    return max(
        height,
        1e-6,
    )


def _thigh_angle_deg(
    frame: FrontSideFrame,
) -> float:
    dx = frame.knee_x - frame.hip_x
    dy = frame.hip_y - frame.knee_y

    return degrees(
        atan2(
            dy,
            dx,
        )
    )


def _shin_angle_deg(
    frame: FrontSideFrame,
) -> float:
    dx = frame.ankle_x - frame.knee_x
    dy = frame.knee_y - frame.ankle_y

    return degrees(
        atan2(
            dy,
            dx,
        )
    )


def _knee_lift_percent(
    frame: FrontSideFrame,
) -> float:
    body_height = _body_height_proxy(
        frame
    )

    lift = max(
        0.0,
        frame.hip_y - frame.knee_y,
    )

    return (
        lift
        / body_height
        * 100.0
    )


def _foot_strike_offset_percent(
    frame: FrontSideFrame,
) -> float:
    body_height = _body_height_proxy(
        frame
    )

    return (
        frame.foot_x
        - frame.com_x
    ) / body_height * 100.0


def _score_metrics(
    *,
    knee_lift_percent: float | None,
    thigh_angle_deg: float | None,
    recovery_velocity_dps: float | None,
    foot_offset_percent: float | None,
    confidence: float | None,
) -> float | None:
    if confidence is None:
        return None

    components: list[float] = []

    if knee_lift_percent is not None:
        components.append(
            _clamp(
                knee_lift_percent / 55.0
            )
        )

    if thigh_angle_deg is not None:
        components.append(
            _clamp(
                (
                    thigh_angle_deg
                    + 10.0
                )
                / 100.0
            )
        )

    if recovery_velocity_dps is not None:
        components.append(
            _clamp(
                recovery_velocity_dps
                / 900.0
            )
        )

    if foot_offset_percent is not None:
        under_com_score = _clamp(
            1.0
            - abs(
                foot_offset_percent
            )
            / 35.0
        )

        components.append(
            under_com_score
        )

    if not components:
        return None

    score = mean(
        components
    )

    score *= _clamp(
        confidence
    )

    return round(
        score * 100.0,
        2,
    )


def analyze_front_side_mechanics(
    frames: list[FrontSideFrame],
    *,
    side: str,
    phase: str,
) -> dict[str, Any]:
    if phase not in SUPPORTED_PHASES:
        return {
            "status": "unsupported_phase",
            "metrics": None,
        }

    selected = [
        frame
        for frame in frames
        if frame.side == side
        and frame.phase == phase
    ]

    if len(selected) < 3:
        return {
            "status": "insufficient_data",
            "metrics": None,
        }

    knee_lifts = [
        _knee_lift_percent(
            frame
        )
        for frame in selected
    ]

    thigh_angles = [
        _thigh_angle_deg(
            frame
        )
        for frame in selected
    ]

    recovery_velocities = [
        abs(
            frame.knee_angular_velocity_dps
        )
        for frame in selected
        if frame.knee_angular_velocity_dps
        is not None
    ]

    foot_offsets = [
        _foot_strike_offset_percent(
            frame
        )
        for frame in selected
    ]

    shin_angles = [
        _shin_angle_deg(
            frame
        )
        for frame in selected
    ]

    confidence = mean(
        _clamp(
            frame.confidence
        )
        for frame in selected
    )

    max_knee_lift = max(
        knee_lifts
    )

    max_thigh_angle = max(
        thigh_angles
    )

    peak_recovery_velocity = (
        max(
            recovery_velocities
        )
        if recovery_velocities
        else None
    )

    average_offset = mean(
        foot_offsets
    )

    average_shin_angle = mean(
        shin_angles
    )

    if average_offset > 20.0:
        overstride_risk = "high"
    elif average_offset > 10.0:
        overstride_risk = "moderate"
    else:
        overstride_risk = "low"

    score = _score_metrics(
        knee_lift_percent=max_knee_lift,
        thigh_angle_deg=max_thigh_angle,
        recovery_velocity_dps=(
            peak_recovery_velocity
        ),
        foot_offset_percent=(
            average_offset
        ),
        confidence=confidence,
    )

    metrics = FrontSideMetrics(
        side=side,
        phase=phase,
        frames_used=len(selected),
        maximum_knee_lift_body_height_percent=round(
            max_knee_lift,
            2,
        ),
        maximum_thigh_angle_deg=round(
            max_thigh_angle,
            2,
        ),
        peak_knee_recovery_velocity_dps=(
            round(
                peak_recovery_velocity,
                2,
            )
            if peak_recovery_velocity
            is not None
            else None
        ),
        average_foot_strike_offset_from_com_percent=round(
            average_offset,
            2,
        ),
        average_shin_angle_before_contact_deg=round(
            average_shin_angle,
            2,
        ),
        overstride_risk=overstride_risk,
        score=score,
        confidence=round(
            confidence * 100.0,
            2,
        ),
    )

    return {
        "status": "experimental",
        "metrics": metrics.to_dict(),
        "limitations": [
            "All angles are projected 2D image-plane measurements.",
            "Foot-strike position is camera-relative and requires side-view footage.",
            "Thresholds are provisional until validated against labelled sprint data.",
        ],
        "engine_version": "0.1.0",
    }
