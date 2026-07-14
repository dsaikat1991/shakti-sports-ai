from typing import Any

import cv2
import numpy as np

from app.services.pose.landmark_usability import landmark_is_usable


MOVEMENT_LANDMARK_INDICES = (
    11,
    12,
    23,
    24,
    25,
    26,
    27,
    28,
)


def calculate_frame_change(
    previous_gray: np.ndarray | None,
    current_frame: np.ndarray,
) -> tuple[float, np.ndarray]:
    current_gray = cv2.cvtColor(
        current_frame,
        cv2.COLOR_BGR2GRAY,
    )

    current_gray = cv2.resize(
        current_gray,
        (320, 180),
        interpolation=cv2.INTER_AREA,
    )

    if previous_gray is None:
        return 0.0, current_gray

    difference = cv2.absdiff(previous_gray, current_gray)

    return float(np.mean(difference)), current_gray


def calculate_pose_movement(
    previous_landmarks: list[Any] | None,
    current_landmarks: list[Any],
    *,
    backend: str = "mediapipe",
) -> float:
    if previous_landmarks is None:
        return 0.0

    distances: list[float] = []

    for index in MOVEMENT_LANDMARK_INDICES:
        if (
            index >= len(previous_landmarks)
            or index >= len(current_landmarks)
        ):
            continue

        previous = previous_landmarks[index]
        current = current_landmarks[index]

        if not (
            landmark_is_usable(previous, backend=backend)
            and landmark_is_usable(current, backend=backend)
        ):
            continue

        delta_x = float(current.x) - float(previous.x)
        delta_y = float(current.y) - float(previous.y)

        distance = (delta_x**2 + delta_y**2) ** 0.5
        distances.append(distance)

    if not distances:
        return 0.0

    return float(np.mean(distances))


def score_pose_movement(average_movement: float) -> float:
    if average_movement < 0.002:
        return 10.0

    if average_movement < 0.005:
        return 35.0

    if average_movement < 0.012:
        return 70.0

    if average_movement <= 0.08:
        return 100.0

    return 70.0