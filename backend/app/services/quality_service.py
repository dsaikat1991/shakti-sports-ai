from __future__ import annotations

from typing import Any

import cv2
import numpy as np


VISIBILITY_THRESHOLD = 0.50
PRESENCE_THRESHOLD = 0.50

# MediaPipe Pose landmark indices.
BODY_GROUPS: dict[str, tuple[int, ...]] = {
    "head": (0,),
    "shoulders": (11, 12),
    "hips": (23, 24),
    "knees": (25, 26),
    "ankles": (27, 28),
    "feet": (31, 32),
}


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _landmark_is_usable(landmark: Any) -> bool:
    visibility = float(getattr(landmark, "visibility", 0.0))
    presence = float(getattr(landmark, "presence", 0.0))

    return (
        visibility >= VISIBILITY_THRESHOLD
        and presence >= PRESENCE_THRESHOLD
        and 0.0 <= float(landmark.x) <= 1.0
        and 0.0 <= float(landmark.y) <= 1.0
    )


def calculate_body_group_visibility(
    landmarks: list[Any],
) -> dict[str, float]:
    scores: dict[str, float] = {}

    for group_name, indices in BODY_GROUPS.items():
        usable_count = sum(
            1
            for index in indices
            if index < len(landmarks)
            and _landmark_is_usable(landmarks[index])
        )

        scores[group_name] = round(
            usable_count / len(indices) * 100,
            2,
        )

    return scores


def calculate_full_body_visibility(
    group_scores: dict[str, float],
) -> float:
    if not group_scores:
        return 0.0

    # Lower-body visibility matters more for sprint biomechanics.
    weights = {
        "head": 0.10,
        "shoulders": 0.15,
        "hips": 0.20,
        "knees": 0.20,
        "ankles": 0.20,
        "feet": 0.15,
    }

    score = sum(
        group_scores.get(group, 0.0) * weight
        for group, weight in weights.items()
    )

    return round(score, 2)


def calculate_brightness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def score_brightness(brightness: float) -> float:
    """
    Provisional heuristic:
    - Very dark frames score poorly.
    - Moderate brightness scores highest.
    - Very bright/washed-out frames lose points.
    """
    if brightness < 30:
        return 10.0

    if brightness < 60:
        return 50.0

    if brightness <= 200:
        return 100.0

    if brightness <= 225:
        return 65.0

    return 25.0


def calculate_sharpness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def score_sharpness(sharpness: float) -> float:
    """
    Provisional heuristic based on Laplacian variance.
    Resolution and scene detail affect this value, so this will be
    calibrated later using real Shakti recordings.
    """
    if sharpness < 20:
        return 15.0

    if sharpness < 50:
        return 45.0

    if sharpness < 100:
        return 75.0

    return 100.0


def calculate_movement(
    previous_gray: np.ndarray | None,
    current_frame: np.ndarray,
) -> tuple[float, np.ndarray]:
    current_gray = cv2.cvtColor(
        current_frame,
        cv2.COLOR_BGR2GRAY,
    )

    # Smaller image keeps the comparison inexpensive.
    current_gray = cv2.resize(
        current_gray,
        (320, 180),
        interpolation=cv2.INTER_AREA,
    )

    if previous_gray is None:
        return 0.0, current_gray

    difference = cv2.absdiff(
        previous_gray,
        current_gray,
    )

    movement_value = float(np.mean(difference))

    return movement_value, current_gray


def score_movement(average_movement: float) -> float:
    """
    Provisional heuristic:
    low difference means almost no visible movement;
    very large difference can indicate excessive camera motion.
    """
    if average_movement < 1.5:
        return 10.0

    if average_movement < 3.0:
        return 45.0

    if average_movement <= 20.0:
        return 100.0

    if average_movement <= 35.0:
        return 70.0

    return 35.0


def score_fps(fps: float) -> float:
    if fps >= 50:
        return 100.0

    if fps >= 29:
        return 85.0

    if fps >= 24:
        return 70.0

    if fps >= 20:
        return 45.0

    return 20.0


def build_quality_result(
    *,
    fps: float,
    detection_rate: float,
    group_visibility_totals: dict[str, float],
    frames_with_pose: int,
    brightness_values: list[float],
    sharpness_values: list[float],
    movement_values: list[float],
) -> dict[str, Any]:
    if frames_with_pose > 0:
        group_visibility = {
            group: round(total / frames_with_pose, 2)
            for group, total in group_visibility_totals.items()
        }
    else:
        group_visibility = {
            group: 0.0
            for group in BODY_GROUPS
        }

    body_visibility_score = calculate_full_body_visibility(
        group_visibility
    )

    average_brightness = (
        float(np.mean(brightness_values))
        if brightness_values
        else 0.0
    )

    average_sharpness = (
        float(np.mean(sharpness_values))
        if sharpness_values
        else 0.0
    )

    average_movement = (
        float(np.mean(movement_values))
        if movement_values
        else 0.0
    )

    lighting_score = score_brightness(average_brightness)
    sharpness_score = score_sharpness(average_sharpness)
    movement_score = score_movement(average_movement)
    fps_quality_score = score_fps(fps)

    detection_score = _clamp(detection_rate)

    overall_score = (
        body_visibility_score * 0.45
        + movement_score * 0.20
        + lighting_score * 0.10
        + sharpness_score * 0.10
        + fps_quality_score * 0.10
        + detection_score * 0.05
    )

    overall_score = round(_clamp(overall_score), 2)

    warnings: list[str] = []
    recommendations: list[str] = []

    if group_visibility["knees"] < 70:
        warnings.append("Knees are not consistently visible.")

    if group_visibility["ankles"] < 70:
        warnings.append("Ankles are not consistently visible.")

    if group_visibility["feet"] < 70:
        warnings.append("Feet are not consistently visible.")

    if body_visibility_score < 70:
        recommendations.append(
            "Move the camera farther away and keep the athlete visible from head to toe."
        )

    if lighting_score < 60:
        warnings.append("Lighting quality is too low or overexposed.")
        recommendations.append(
            "Record in brighter, evenly distributed lighting."
        )

    if sharpness_score < 60:
        warnings.append("The recording appears blurred or out of focus.")
        recommendations.append(
            "Keep the camera stable and clean the camera lens before recording."
        )

    if movement_score < 50:
        warnings.append("Very little athletic movement was detected.")
        recommendations.append(
            "Upload an actual performance attempt rather than a standing pose."
        )

    if average_movement > 35:
        warnings.append(
            "Excessive frame movement may indicate a shaky camera."
        )
        recommendations.append(
            "Place the phone on a tripod or stable surface."
        )

    if fps < 24:
        warnings.append("The frame rate is too low for reliable motion analysis.")
        recommendations.append(
            "Record at 30 FPS or higher. Use 60 FPS when available."
        )

    if overall_score >= 85:
        rating = "Excellent"
    elif overall_score >= 70:
        rating = "Good"
    elif overall_score >= 50:
        rating = "Needs Improvement"
    else:
        rating = "Unsuitable"

    biomechanics_ready = (
        overall_score >= 70
        and body_visibility_score >= 75
        and group_visibility["knees"] >= 70
        and group_visibility["ankles"] >= 70
        and group_visibility["feet"] >= 70
        and movement_score >= 50
    )

    return {
        "overall_score": overall_score,
        "rating": rating,
        "biomechanics_ready": biomechanics_ready,
        "metrics": {
            "pose_detection_score": round(detection_score, 2),
            "full_body_visibility_score": body_visibility_score,
            "lighting_score": round(lighting_score, 2),
            "sharpness_score": round(sharpness_score, 2),
            "movement_score": round(movement_score, 2),
            "frame_rate_score": round(fps_quality_score, 2),
        },
        "body_visibility": group_visibility,
        "raw_measurements": {
            "average_brightness": round(average_brightness, 2),
            "average_sharpness": round(average_sharpness, 2),
            "average_frame_difference": round(average_movement, 2),
            "fps": round(fps, 2),
        },
        "warnings": warnings,
        "recommendations": recommendations,
    }