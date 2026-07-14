from typing import Any

import cv2
import mediapipe as mp

from app.services.biomechanics.angles import (
    calculate_frame_joint_angles,
)
from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)
from app.services.pose.detector import create_pose_landmarker
from app.services.pose.serializer import serialize_landmarks
from app.services.quality.frame_quality import (
    calculate_brightness,
    calculate_sharpness,
)
from app.services.quality.movement import (
    calculate_frame_change,
    calculate_pose_movement,
)
from app.services.quality.orientation import classify_camera_view
from app.services.quality.scoring import build_quality_result
from app.services.quality.visibility import (
    BODY_GROUPS,
    calculate_athlete_bounding_box,
    calculate_body_group_visibility,
)


QUALITY_FRAME_SAMPLE_RATE = 5
BIOMECHANICS_FRAME_SAMPLE_RATE = 1
MAX_SAMPLE_LANDMARK_FRAMES = 5


def analyze_video(video_path: str) -> dict[str, Any]:
    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError("Could not open uploaded video.")

    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))

    if fps <= 0:
        capture.release()
        raise ValueError("Invalid video FPS.")

    duration_seconds = total_frames / fps if total_frames > 0 else 0.0

    quality_frames_sampled = 0
    biomechanics_frames_processed = 0
    frames_with_pose = 0
    frame_index = 0
    landmark_count_total = 0

    landmark_samples: list[dict[str, Any]] = []
    all_frame_metrics: list[FrameMetrics] = []

    group_visibility_totals = {
        group: 0.0
        for group in BODY_GROUPS
    }

    brightness_values: list[float] = []
    sharpness_values: list[float] = []
    frame_change_values: list[float] = []
    pose_movement_values: list[float] = []
    occupancy_values: list[float] = []
    headroom_values: list[float] = []
    camera_view_results: list[dict[str, Any]] = []

    previous_gray = None
    previous_landmarks = None

    try:
        with create_pose_landmarker() as landmarker:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                if (
                    frame_index
                    % BIOMECHANICS_FRAME_SAMPLE_RATE
                    != 0
                ):
                    frame_index += 1
                    continue

                biomechanics_frames_processed += 1

                is_quality_frame = (
                    frame_index
                    % QUALITY_FRAME_SAMPLE_RATE
                    == 0
                )

                if is_quality_frame:
                    quality_frames_sampled += 1
                    brightness_values.append(
                        calculate_brightness(frame)
                    )
                    sharpness_values.append(
                        calculate_sharpness(frame)
                    )

                    frame_change, previous_gray = (
                        calculate_frame_change(
                            previous_gray,
                            frame,
                        )
                    )

                    if quality_frames_sampled > 1:
                        frame_change_values.append(
                            frame_change
                        )

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )

                timestamp_ms = int(
                    (frame_index / fps) * 1000
                )

                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms,
                )

                if result.pose_landmarks:
                    frames_with_pose += 1
                    first_pose = result.pose_landmarks[0]
                    landmark_count_total += len(first_pose)

                    joint_angles = (
                        calculate_frame_joint_angles(
                            first_pose
                        )
                    )

                    group_scores = (
                        calculate_body_group_visibility(
                            first_pose
                        )
                    )

                    for group, score in group_scores.items():
                        group_visibility_totals[group] += score

                    bounding_box = (
                        calculate_athlete_bounding_box(
                            first_pose
                        )
                    )

                    if bounding_box:
                        occupancy_values.append(
                            bounding_box["area_percent"]
                        )
                        headroom_values.append(
                            bounding_box["y_min"]
                        )

                    pose_movement = calculate_pose_movement(
                        previous_landmarks,
                        first_pose,
                    )

                    if previous_landmarks is not None:
                        pose_movement_values.append(
                            pose_movement
                        )

                    previous_landmarks = first_pose

                    camera_view = classify_camera_view(
                        first_pose
                    )
                    camera_view_results.append(
                        camera_view
                    )

                    all_frame_metrics.append(
                        FrameMetrics(
                            frame_index=frame_index,
                            timestamp_ms=timestamp_ms,
                            joint_angles=joint_angles,
                            bounding_box=bounding_box,
                            camera_view=camera_view,
                            landmarks=tuple(first_pose),
                        )
                    )

                    if (
                        len(landmark_samples)
                        < MAX_SAMPLE_LANDMARK_FRAMES
                    ):
                        landmark_samples.append(
                            {
                                "frame_index": frame_index,
                                "timestamp_ms": timestamp_ms,
                                "bounding_box": bounding_box,
                                "camera_view": camera_view,
                                "joint_angles": joint_angles,
                                "landmarks": serialize_landmarks(
                                    first_pose
                                ),
                            }
                        )

                frame_index += 1

    finally:
        capture.release()

    detection_rate = (
        frames_with_pose
        / biomechanics_frames_processed
        * 100
        if biomechanics_frames_processed > 0
        else 0.0
    )

    average_landmarks = (
        landmark_count_total / frames_with_pose
        if frames_with_pose > 0
        else 0.0
    )

    recording_quality = build_quality_result(
        fps=fps,
        detection_rate=detection_rate,
        group_visibility_totals=group_visibility_totals,
        frames_with_pose=frames_with_pose,
        brightness_values=brightness_values,
        sharpness_values=sharpness_values,
        pose_movement_values=pose_movement_values,
        frame_change_values=frame_change_values,
        occupancy_values=occupancy_values,
        headroom_values=headroom_values,
        camera_view_results=camera_view_results,
    )

    readiness = recording_quality.get(
        "analysis_readiness",
        {},
    )

    biomechanics = build_sprint_biomechanics_preview(
        all_frame_metrics,
        analysis_ready=bool(
            readiness.get("ready", False)
        ),
        readiness_reason=str(
            readiness.get(
                "rating",
                "Recording did not pass the analysis-readiness gate.",
            )
        ),
    )

    return {
        "video": {
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration_seconds": round(
                duration_seconds,
                2,
            ),
        },
        "analysis": {
            "quality_frame_sample_rate": (
                QUALITY_FRAME_SAMPLE_RATE
            ),
            "biomechanics_frame_sample_rate": (
                BIOMECHANICS_FRAME_SAMPLE_RATE
            ),
            "quality_frames_sampled": (
                quality_frames_sampled
            ),
            "biomechanics_frames_processed": (
                biomechanics_frames_processed
            ),
            "frames_with_pose": frames_with_pose,
            "detection_rate_percent": round(
                detection_rate,
                2,
            ),
            "average_landmarks_detected": round(
                average_landmarks,
                2,
            ),
        },
        "recording_quality": recording_quality,
        "analysis_summary": {
            "frames_available_for_biomechanics": len(
                all_frame_metrics
            ),
        },
        "biomechanics": biomechanics,
        "landmark_samples": landmark_samples,
    }
