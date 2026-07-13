from __future__ import annotations

from typing import Any

from app.services.pose.landmark_usability import landmark_is_usable

LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_HIP = 23
RIGHT_HIP = 24


def _is_reliable(
    landmark: Any,
    *,
    backend: str = "mediapipe",
) -> bool:
    x = float(getattr(landmark, "x", -1.0))
    y = float(getattr(landmark, "y", -1.0))

    return (
        landmark_is_usable(
            landmark,
            backend=backend,
        )
        and 0.0 <= x <= 1.0
        and 0.0 <= y <= 1.0
    )


def _distance_2d(first: Any, second: Any) -> float:
    delta_x = float(first.x) - float(second.x)
    delta_y = float(first.y) - float(second.y)
    return (delta_x**2 + delta_y**2) ** 0.5


def classify_camera_view(
    landmarks: list[Any],
    *,
    backend: str = "mediapipe",
) -> dict[str, Any]:
    required_indices = (
        LEFT_SHOULDER,
        RIGHT_SHOULDER,
        LEFT_HIP,
        RIGHT_HIP,
    )

    if any(index >= len(landmarks) for index in required_indices):
        return {
            "view": "Unknown",
            "confidence": 0.0,
            "suitable_for_sprint": False,
            "reason": "Required torso landmarks are missing.",
            "measurements": None,
            "pose_backend": backend,
        }

    left_shoulder = landmarks[LEFT_SHOULDER]
    right_shoulder = landmarks[RIGHT_SHOULDER]
    left_hip = landmarks[LEFT_HIP]
    right_hip = landmarks[RIGHT_HIP]

    torso_landmarks = (
        left_shoulder,
        right_shoulder,
        left_hip,
        right_hip,
    )

    if not all(
        _is_reliable(item, backend=backend)
        for item in torso_landmarks
    ):
        return {
            "view": "Unknown",
            "confidence": 0.0,
            "suitable_for_sprint": False,
            "reason": (
                "Torso landmarks are not reliable enough under the "
                f"{backend} pose-quality policy."
            ),
            "measurements": None,
            "pose_backend": backend,
        }

    shoulder_width = _distance_2d(left_shoulder, right_shoulder)
    hip_width = _distance_2d(left_hip, right_hip)

    shoulder_midpoint_y = (
        float(left_shoulder.y) + float(right_shoulder.y)
    ) / 2.0
    hip_midpoint_y = (
        float(left_hip.y) + float(right_hip.y)
    ) / 2.0
    torso_height = abs(hip_midpoint_y - shoulder_midpoint_y)

    if torso_height < 0.03:
        return {
            "view": "Unknown",
            "confidence": 0.0,
            "suitable_for_sprint": False,
            "reason": "Torso height is too small for orientation assessment.",
            "measurements": None,
            "pose_backend": backend,
        }

    average_body_width = (shoulder_width + hip_width) / 2.0
    width_to_torso_ratio = average_body_width / torso_height

    if width_to_torso_ratio <= 0.55:
        view = "Side View"
        suitable_for_sprint = True
        confidence = min(
            100.0,
            70.0 + (0.55 - width_to_torso_ratio) * 100.0,
        )
    elif width_to_torso_ratio <= 0.95:
        view = "Three-Quarter View"
        suitable_for_sprint = False
        distance_from_center = abs(width_to_torso_ratio - 0.75)
        confidence = max(
            55.0,
            80.0 - distance_from_center * 100.0,
        )
    else:
        view = "Front View"
        suitable_for_sprint = False
        confidence = min(
            100.0,
            65.0 + (width_to_torso_ratio - 0.95) * 50.0,
        )

    return {
        "view": view,
        "confidence": round(confidence, 2),
        "suitable_for_sprint": suitable_for_sprint,
        "reason": "Orientation estimated from shoulder and hip separation.",
        "measurements": {
            "shoulder_width": round(shoulder_width, 5),
            "hip_width": round(hip_width, 5),
            "torso_height": round(torso_height, 5),
            "width_to_torso_ratio": round(
                width_to_torso_ratio,
                5,
            ),
        },
        "pose_backend": backend,
    }
