from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics


LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32

MIN_CONFIDENCE = 0.50


@dataclass(slots=True, frozen=True)
class SideSignalSample:
    side: str
    frame_index: int
    timestamp_ms: int
    foot_x: float
    foot_y: float
    foot_vx: float
    foot_vy: float
    foot_speed: float
    ankle_acceleration: float
    knee_angle: float | None
    knee_angular_velocity: float | None
    hip_y: float | None
    hip_vy: float | None
    com_y: float | None
    com_vy: float | None


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


def _mean_point(
    landmarks: tuple[Any, ...],
    indices: tuple[int, ...],
) -> tuple[float, float] | None:
    points = [
        landmarks[index]
        for index in indices
        if index < len(landmarks)
        and _is_reliable(landmarks[index])
    ]

    if not points:
        return None

    return (
        float(np.mean([_value(point, "x") for point in points])),
        float(np.mean([_value(point, "y") for point in points])),
    )


def _com_y(frame: FrameMetrics) -> float | None:
    torso = _mean_point(
        frame.landmarks,
        (
            LEFT_HIP,
            RIGHT_HIP,
            LEFT_KNEE,
            RIGHT_KNEE,
        ),
    )

    if torso is None:
        return None

    return torso[1]


def _derivative(
    current_value: float | None,
    previous_value: float | None,
    dt_seconds: float,
) -> float | None:
    if (
        current_value is None
        or previous_value is None
        or dt_seconds <= 0
    ):
        return None

    return (current_value - previous_value) / dt_seconds


def extract_side_signals(
    frame_metrics: list[FrameMetrics],
    side: str,
) -> list[SideSignalSample]:
    if side not in ("left", "right"):
        raise ValueError("side must be 'left' or 'right'.")

    if side == "left":
        ankle_index = LEFT_ANKLE
        heel_index = LEFT_HEEL
        foot_index = LEFT_FOOT_INDEX
        hip_index = LEFT_HIP
        knee_angle_name = "left_knee"
    else:
        ankle_index = RIGHT_ANKLE
        heel_index = RIGHT_HEEL
        foot_index = RIGHT_FOOT_INDEX
        hip_index = RIGHT_HIP
        knee_angle_name = "right_knee"

    result: list[SideSignalSample] = []

    previous_foot: tuple[float, float] | None = None
    previous_foot_velocity: tuple[float, float] | None = None
    previous_knee_angle: float | None = None
    previous_hip_y: float | None = None
    previous_com_y: float | None = None
    previous_timestamp_ms: int | None = None

    for frame in frame_metrics:
        foot = _mean_point(
            frame.landmarks,
            (
                ankle_index,
                heel_index,
                foot_index,
            ),
        )

        if foot is None:
            continue

        hip_y = None

        if (
            hip_index < len(frame.landmarks)
            and _is_reliable(frame.landmarks[hip_index])
        ):
            hip_y = _value(
                frame.landmarks[hip_index],
                "y",
            )

        current_com_y = _com_y(frame)
        knee_angle = frame.joint_angles.get(
            knee_angle_name
        )

        dt_seconds = (
            (
                frame.timestamp_ms
                - previous_timestamp_ms
            )
            / 1000.0
            if previous_timestamp_ms is not None
            else 0.0
        )

        foot_vx = _derivative(
            foot[0],
            previous_foot[0] if previous_foot else None,
            dt_seconds,
        )

        foot_vy = _derivative(
            foot[1],
            previous_foot[1] if previous_foot else None,
            dt_seconds,
        )

        if foot_vx is None or foot_vy is None:
            foot_speed = 0.0
        else:
            foot_speed = (
                foot_vx**2 + foot_vy**2
            ) ** 0.5

        if (
            previous_foot_velocity is None
            or foot_vx is None
            or foot_vy is None
            or dt_seconds <= 0
        ):
            ankle_acceleration = 0.0
        else:
            acceleration_x = (
                foot_vx
                - previous_foot_velocity[0]
            ) / dt_seconds

            acceleration_y = (
                foot_vy
                - previous_foot_velocity[1]
            ) / dt_seconds

            ankle_acceleration = (
                acceleration_x**2
                + acceleration_y**2
            ) ** 0.5

        knee_angular_velocity = _derivative(
            float(knee_angle)
            if knee_angle is not None
            else None,
            previous_knee_angle,
            dt_seconds,
        )

        hip_vy = _derivative(
            hip_y,
            previous_hip_y,
            dt_seconds,
        )

        com_vy = _derivative(
            current_com_y,
            previous_com_y,
            dt_seconds,
        )

        result.append(
            SideSignalSample(
                side=side,
                frame_index=frame.frame_index,
                timestamp_ms=frame.timestamp_ms,
                foot_x=foot[0],
                foot_y=foot[1],
                foot_vx=foot_vx or 0.0,
                foot_vy=foot_vy or 0.0,
                foot_speed=foot_speed,
                ankle_acceleration=ankle_acceleration,
                knee_angle=(
                    float(knee_angle)
                    if knee_angle is not None
                    else None
                ),
                knee_angular_velocity=(
                    knee_angular_velocity
                ),
                hip_y=hip_y,
                hip_vy=hip_vy,
                com_y=current_com_y,
                com_vy=com_vy,
            )
        )

        previous_foot = foot

        if foot_vx is not None and foot_vy is not None:
            previous_foot_velocity = (
                foot_vx,
                foot_vy,
            )

        previous_knee_angle = (
            float(knee_angle)
            if knee_angle is not None
            else None
        )
        previous_hip_y = hip_y
        previous_com_y = current_com_y
        previous_timestamp_ms = frame.timestamp_ms

    return result
