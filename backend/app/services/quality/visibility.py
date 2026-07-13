from __future__ import annotations

from typing import Any

from app.services.pose.landmark_usability import (
    landmark_is_usable as backend_landmark_is_usable,
)

VISIBILITY_THRESHOLD = 0.50
PRESENCE_THRESHOLD = 0.50

BODY_GROUPS: dict[str, tuple[int, ...]] = {
    "head": (0,),
    "shoulders": (11, 12),
    "hips": (23, 24),
    "knees": (25, 26),
    "ankles": (27, 28),
    "feet": (31, 32),
}

BODY_GROUP_WEIGHTS: dict[str, float] = {
    "head": 0.10,
    "shoulders": 0.15,
    "hips": 0.20,
    "knees": 0.20,
    "ankles": 0.20,
    "feet": 0.15,
}


def landmark_is_usable(
    landmark: Any,
    *,
    backend: str = "mediapipe",
) -> bool:
    x = float(getattr(landmark, "x", -1.0))
    y = float(getattr(landmark, "y", -1.0))

    return (
        backend_landmark_is_usable(
            landmark,
            backend=backend,
        )
        and 0.0 <= x <= 1.0
        and 0.0 <= y <= 1.0
    )


def calculate_body_group_visibility(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
) -> dict[str, float]:
    result: dict[str, float] = {}

    for group_name, indices in BODY_GROUPS.items():
        usable_count = sum(
            1
            for index in indices
            if index < len(landmarks)
            and landmark_is_usable(
                landmarks[index],
                backend=backend,
            )
        )

        result[group_name] = round(
            usable_count / len(indices) * 100.0,
            2,
        )

    return result


def calculate_full_body_visibility(
    group_scores: dict[str, float],
) -> float:
    score = sum(
        group_scores.get(group, 0.0) * weight
        for group, weight in BODY_GROUP_WEIGHTS.items()
    )
    return round(score, 2)


def calculate_athlete_bounding_box(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
) -> dict[str, float] | None:
    usable_landmarks = [
        landmark
        for landmark in landmarks
        if landmark_is_usable(
            landmark,
            backend=backend,
        )
    ]

    if len(usable_landmarks) < 4:
        return None

    x_values = [float(landmark.x) for landmark in usable_landmarks]
    y_values = [float(landmark.y) for landmark in usable_landmarks]

    x_min = max(0.0, min(x_values))
    x_max = min(1.0, max(x_values))
    y_min = max(0.0, min(y_values))
    y_max = min(1.0, max(y_values))

    width = max(0.0, x_max - x_min)
    height = max(0.0, y_max - y_min)
    area = width * height

    return {
        "x_min": round(x_min, 4),
        "y_min": round(y_min, 4),
        "x_max": round(x_max, 4),
        "y_max": round(y_max, 4),
        "width": round(width, 4),
        "height": round(height, 4),
        "area_percent": round(area * 100.0, 2),
    }
