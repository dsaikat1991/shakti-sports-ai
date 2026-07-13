from __future__ import annotations

from typing import Any

import numpy as np

from app.services.quality.frame_quality import (
    score_brightness,
    score_fps,
    score_sharpness,
)
from app.services.quality.movement import score_pose_movement
from app.services.quality.visibility import (
    BODY_GROUPS,
    calculate_full_body_visibility,
)


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(minimum, min(maximum, value))


def _calculate_dominant_camera_view(
    camera_view_results: list[dict[str, Any]],
) -> tuple[str, float]:
    known_results = [
        result
        for result in camera_view_results
        if result.get("view") not in (None, "Unknown")
    ]

    if not known_results:
        return "Unknown", 0.0

    view_counts: dict[str, int] = {}

    for result in known_results:
        view = str(result["view"])
        view_counts[view] = view_counts.get(view, 0) + 1

    dominant_view = max(
        view_counts,
        key=lambda view: view_counts[view],
    )

    matching_results = [
        result
        for result in known_results
        if result.get("view") == dominant_view
    ]

    confidence_values = [
        float(result.get("confidence", 0.0))
        for result in matching_results
    ]

    average_confidence = (
        float(np.mean(confidence_values))
        if confidence_values
        else 0.0
    )

    return dominant_view, average_confidence


def _camera_angle_score(view: str) -> float:
    if view == "Side View":
        return 100.0

    if view == "Three-Quarter View":
        return 55.0

    if view == "Front View":
        return 25.0

    return 0.0


def _recording_quality_rating(score: float) -> str:
    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Needs Improvement"

    return "Unsuitable"


def _readiness_rating(
    *,
    biomechanics_ready: bool,
    dominant_view: str,
    full_body_score: float,
    movement_score: float,
    readiness_score: float,
) -> str:
    if biomechanics_ready:
        return "Ready for Sprint Analysis"

    if dominant_view == "Front View":
        return "Unsuitable Camera Angle"

    if dominant_view == "Three-Quarter View":
        return "Move to a Side View"

    if dominant_view == "Unknown":
        return "Camera Angle Unclear"

    if full_body_score < 75:
        return "Full Body Not Visible"

    if movement_score < 50:
        return "Insufficient Athletic Movement"

    if readiness_score >= 70:
        return "Review Required"

    return "Not Ready for Analysis"


def build_quality_result(
    *,
    fps: float,
    detection_rate: float,
    group_visibility_totals: dict[str, float],
    frames_with_pose: int,
    brightness_values: list[float],
    sharpness_values: list[float],
    pose_movement_values: list[float],
    frame_change_values: list[float],
    occupancy_values: list[float],
    camera_view_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the Shakti Recording Quality Assessment result.

    Recording quality and sport-specific analysis readiness are deliberately
    scored separately.

    A video may be clear, sharp, and well-lit while still being unsuitable
    for sprint biomechanics because of its camera angle or incomplete body
    visibility.
    """

    if frames_with_pose > 0:
        group_visibility = {
            group: round(
                group_visibility_totals.get(group, 0.0)
                / frames_with_pose,
                2,
            )
            for group in BODY_GROUPS
        }
    else:
        group_visibility = {
            group: 0.0
            for group in BODY_GROUPS
        }

    full_body_score = calculate_full_body_visibility(
        group_visibility
    )

    lower_body_visible = (
        group_visibility["hips"] >= 50
        and group_visibility["knees"] >= 50
        and group_visibility["ankles"] >= 50
    )

    feet_visible = group_visibility["feet"] >= 50

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

    average_pose_movement = (
        float(np.mean(pose_movement_values))
        if pose_movement_values
        else 0.0
    )

    average_frame_change = (
        float(np.mean(frame_change_values))
        if frame_change_values
        else 0.0
    )

    average_occupancy = (
        float(np.mean(occupancy_values))
        if occupancy_values
        else 0.0
    )

    minimum_occupancy = (
        float(np.min(occupancy_values))
        if occupancy_values
        else 0.0
    )

    maximum_occupancy = (
        float(np.max(occupancy_values))
        if occupancy_values
        else 0.0
    )

    lighting_score = score_brightness(
        average_brightness
    )

    sharpness_score = score_sharpness(
        average_sharpness
    )

    fps_score = score_fps(fps)

    detection_score = _clamp(
        detection_rate
    )

    if lower_body_visible:
        movement_score = score_pose_movement(
            average_pose_movement
        )
    else:
        movement_score = 0.0

    if full_body_score < 60:
        occupancy_score = 0.0

    elif 15 <= average_occupancy <= 65:
        occupancy_score = 100.0

    elif 8 <= average_occupancy < 15:
        occupancy_score = 65.0

    elif 65 < average_occupancy <= 80:
        occupancy_score = 65.0

    else:
        occupancy_score = 25.0

    dominant_view, camera_view_confidence = (
        _calculate_dominant_camera_view(
            camera_view_results
        )
    )

    camera_angle_score = _camera_angle_score(
        dominant_view
    )

    #
    # General recording-quality score
    #
    # This measures technical recording quality and does not punish a clear
    # front-facing video merely because it is unsuitable for side-view sprint
    # biomechanics.
    #

    recording_quality_score = (
        detection_score * 0.20
        + lighting_score * 0.20
        + sharpness_score * 0.20
        + fps_score * 0.15
        + full_body_score * 0.15
        + occupancy_score * 0.10
    )

    if full_body_score < 40:
        recording_quality_score = min(
            recording_quality_score,
            59.0,
        )

    recording_quality_score = round(
        _clamp(recording_quality_score),
        2,
    )

    recording_quality_rating = (
        _recording_quality_rating(
            recording_quality_score
        )
    )

    #
    # Sprint-analysis readiness score
    #
    # This is sport-specific and heavily considers camera orientation,
    # lower-body visibility, movement and athlete framing.
    #

    analysis_readiness_score = (
        full_body_score * 0.30
        + movement_score * 0.20
        + occupancy_score * 0.10
        + camera_angle_score * 0.25
        + detection_score * 0.10
        + fps_score * 0.05
    )

    if not lower_body_visible or not feet_visible:
        analysis_readiness_score = min(
            analysis_readiness_score,
            49.0,
        )

    if dominant_view == "Front View":
        analysis_readiness_score = min(
            analysis_readiness_score,
            35.0,
        )

    elif dominant_view == "Three-Quarter View":
        analysis_readiness_score = min(
            analysis_readiness_score,
            60.0,
        )

    elif dominant_view == "Unknown":
        analysis_readiness_score = min(
            analysis_readiness_score,
            45.0,
        )

    analysis_readiness_score = round(
        _clamp(analysis_readiness_score),
        2,
    )

    biomechanics_ready = (
        analysis_readiness_score >= 70
        and full_body_score >= 75
        and group_visibility["hips"] >= 70
        and group_visibility["knees"] >= 70
        and group_visibility["ankles"] >= 70
        and group_visibility["feet"] >= 70
        and movement_score >= 50
        and dominant_view == "Side View"
    )

    readiness_rating = _readiness_rating(
        biomechanics_ready=biomechanics_ready,
        dominant_view=dominant_view,
        full_body_score=full_body_score,
        movement_score=movement_score,
        readiness_score=analysis_readiness_score,
    )

    warnings: list[str] = []
    recommendations: list[str] = []

    if group_visibility["hips"] < 70:
        warnings.append(
            "Hips are not consistently visible."
        )

    if group_visibility["knees"] < 70:
        warnings.append(
            "Knees are not consistently visible."
        )

    if group_visibility["ankles"] < 70:
        warnings.append(
            "Ankles are not consistently visible."
        )

    if group_visibility["feet"] < 70:
        warnings.append(
            "Feet are not consistently visible."
        )

    if full_body_score < 70:
        recommendations.append(
            "Move the camera farther away and keep the athlete visible from head to toe."
        )

    if not lower_body_visible:
        warnings.append(
            "Athlete movement could not be assessed because the lower body is not reliably visible."
        )

    if full_body_score < 60:
        warnings.append(
            "Camera distance could not be assessed reliably from a partial-body recording."
        )

    if lower_body_visible and movement_score < 50:
        warnings.append(
            "Very little reliable athlete movement was detected."
        )

        recommendations.append(
            "Upload an actual performance attempt rather than a standing pose."
        )

    if full_body_score >= 60 and average_occupancy > 80:
        warnings.append(
            "The athlete appears too close to the camera."
        )

        recommendations.append(
            "Move the camera farther away while keeping the full body visible."
        )

    if full_body_score >= 60 and 0 < average_occupancy < 8:
        warnings.append(
            "The athlete appears too far from the camera."
        )

        recommendations.append(
            "Move the camera closer while keeping the full body visible."
        )

    if lighting_score < 60:
        warnings.append(
            "Lighting quality is unsuitable."
        )

        recommendations.append(
            "Record in brighter and more evenly distributed lighting."
        )

    if sharpness_score < 60:
        warnings.append(
            "The recording appears blurred or out of focus."
        )

        recommendations.append(
            "Keep the camera stable and clean the camera lens."
        )

    if fps < 24:
        warnings.append(
            "The frame rate is too low for reliable biomechanics."
        )

        recommendations.append(
            "Record at 30 FPS or higher."
        )

    if average_frame_change > 35:
        warnings.append(
            "Large visual changes may indicate excessive camera shake or background movement."
        )

        recommendations.append(
            "Use a tripod or place the phone on a stable surface."
        )

    if dominant_view == "Front View":
        warnings.append(
            "The athlete appears to be facing the camera."
        )

        recommendations.append(
            "For sprint analysis, record from a stable side-on position."
        )

    elif dominant_view == "Three-Quarter View":
        warnings.append(
            "The recording appears to use a three-quarter camera angle."
        )

        recommendations.append(
            "Move the camera to a clearer side-on position."
        )

    elif dominant_view == "Unknown":
        warnings.append(
            "Camera orientation could not be assessed reliably."
        )

        recommendations.append(
            "Record the athlete's full body from a clear side-on position."
        )

    return {
        # Kept for compatibility with the present response structure.
        "overall_score": recording_quality_score,
        "rating": recording_quality_rating,
        "biomechanics_ready": biomechanics_ready,

        "analysis_readiness": {
            "score": analysis_readiness_score,
            "rating": readiness_rating,
            "ready": biomechanics_ready,
            "required_camera_view": "Side View",
        },

        "metrics": {
            "pose_detection_score": round(
                detection_score,
                2,
            ),
            "full_body_visibility_score": full_body_score,
            "athlete_movement_score": (
                round(movement_score, 2)
                if lower_body_visible
                else None
            ),
            "athlete_occupancy_score": (
                round(occupancy_score, 2)
                if full_body_score >= 60
                else None
            ),
            "camera_angle_score": (
                round(camera_angle_score, 2)
                if dominant_view != "Unknown"
                else None
            ),
            "lighting_score": round(
                lighting_score,
                2,
            ),
            "sharpness_score": round(
                sharpness_score,
                2,
            ),
            "frame_rate_score": round(
                fps_score,
                2,
            ),
        },

        "body_visibility": group_visibility,

        "camera_view": {
            "classification": dominant_view,
            "confidence": round(
                camera_view_confidence,
                2,
            ),
            "suitable_for_sprint": (
                dominant_view == "Side View"
            ),
            "required_view": "Side View",
        },

        "raw_measurements": {
            "average_brightness": round(
                average_brightness,
                2,
            ),
            "average_sharpness": round(
                average_sharpness,
                2,
            ),
            "average_pose_movement": round(
                average_pose_movement,
                6,
            ),
            "average_frame_change": round(
                average_frame_change,
                2,
            ),
            "average_athlete_occupancy_percent": round(
                average_occupancy,
                2,
            ),
            "athlete_occupancy_range_percent": {
                "minimum": round(
                    minimum_occupancy,
                    2,
                ),
                "maximum": round(
                    maximum_occupancy,
                    2,
                ),
                "average": round(
                    average_occupancy,
                    2,
                ),
            },
            "fps": round(
                fps,
                2,
            ),
        },

        "warnings": warnings,
        "recommendations": recommendations,
    }