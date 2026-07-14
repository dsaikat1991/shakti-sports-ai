from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np

from app.services.pose_remote.athlete_selection import AthleteTracker
from app.services.pose_remote.biomechanics_bridge import (
    analyze_sprint_stream,
    pose_frame_to_frame_metrics,
)
from app.services.pose_remote.client import RTMPoseWorkerClient
from app.services.pose_remote.pose_stream import timeline_to_pose_stream
from app.services.pose_remote.video_pipeline import analyze_video_with_tracking
from app.services.quality.frame_quality import calculate_brightness, calculate_sharpness
from app.services.quality.movement import calculate_frame_change, calculate_pose_movement
from app.services.quality.scoring import build_quality_result
from app.services.quality.visibility import BODY_GROUPS, calculate_body_group_visibility
from app.services.reports.sprint_segment_report import build_sprint_stream_report

RTMPOSE_WORKER_URL = os.getenv("RTMPOSE_WORKER_URL", "http://127.0.0.1:8011")

# Every Nth frame sampled for pure image-quality signals (brightness,
# sharpness, frame-to-frame change) - these are cheap, GPU-free cv2
# calls, unlike pose inference, so this pass is fast regardless of clip
# length and runs before committing to the full RTMPose pass.
QUALITY_FRAME_SAMPLE_RATE = 5


def _collect_image_quality(video_path: str) -> dict[str, list[float]]:
    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError("Could not open uploaded video.")

    brightness_values: list[float] = []
    sharpness_values: list[float] = []
    frame_change_values: list[float] = []
    previous_gray: np.ndarray | None = None
    frame_index = 0

    try:
        while True:
            grabbed, frame = capture.read()

            if not grabbed:
                break

            if frame_index % QUALITY_FRAME_SAMPLE_RATE == 0:
                brightness_values.append(calculate_brightness(frame))
                sharpness_values.append(calculate_sharpness(frame))

                change, previous_gray = calculate_frame_change(
                    previous_gray, frame
                )

                if len(brightness_values) > 1:
                    frame_change_values.append(change)

            frame_index += 1
    finally:
        capture.release()

    return {
        "brightness_values": brightness_values,
        "sharpness_values": sharpness_values,
        "frame_change_values": frame_change_values,
    }


def _connect_worker() -> RTMPoseWorkerClient:
    client = RTMPoseWorkerClient(base_url=RTMPOSE_WORKER_URL)

    try:
        health = client.health()
    except Exception as error:
        raise RuntimeError(
            "RTMPose worker is not reachable at "
            f"{RTMPOSE_WORKER_URL}. Start it with "
            "'uvicorn rtmpose_worker.app:app --port 8011' before "
            "submitting videos for analysis."
        ) from error

    if not health.get("initialized"):
        client.initialize()

    return client


def analyze_video(video_path: str) -> dict[str, Any]:
    """
    RTMPose-backed pose analysis, matching the interface of
    app.services.pose.analyzer.analyze_video.

    Unlike the MediaPipe path, pose inference happens in a separate,
    GPU-backed worker process reached over HTTP - _connect_worker
    raises a clear, actionable error (surfaced as a failed job, not a
    server crash) if that worker isn't running.
    """
    image_quality = _collect_image_quality(video_path)

    client = _connect_worker()
    tracker = AthleteTracker(width=0, height=0)
    timeline = analyze_video_with_tracking(
        video_path,
        worker=client,
        tracker=tracker,
    )

    video_info = timeline.get("video", {})
    fps = float(video_info.get("fps") or 0.0)
    total_frames = int(video_info.get("total_frames") or 0)
    duration_seconds = total_frames / fps if fps > 0 else 0.0

    stream = timeline_to_pose_stream(timeline)
    frame_metrics = [
        pose_frame_to_frame_metrics(frame) for frame in stream.frames
    ]

    group_visibility_totals = {group: 0.0 for group in BODY_GROUPS}
    occupancy_values: list[float] = []
    headroom_values: list[float] = []
    camera_view_results: list[dict[str, Any]] = []
    pose_movement_values: list[float] = []
    previous_landmarks: list[Any] | None = None

    for frame in frame_metrics:
        backend = getattr(frame, "backend", "rtmpose")
        landmarks = list(frame.landmarks)

        group_scores = calculate_body_group_visibility(
            landmarks, backend=backend
        )
        for group, score in group_scores.items():
            group_visibility_totals[group] += score

        if frame.bounding_box:
            occupancy_values.append(frame.bounding_box["area_percent"])
            headroom_values.append(frame.bounding_box["y_min"])

        camera_view_results.append(frame.camera_view)

        if previous_landmarks is not None:
            pose_movement_values.append(
                calculate_pose_movement(
                    previous_landmarks, landmarks, backend=backend
                )
            )
        previous_landmarks = landmarks

    frames_with_pose = len(frame_metrics)
    detection_rate = (
        frames_with_pose / total_frames * 100.0
        if total_frames > 0
        else 0.0
    )

    recording_quality = build_quality_result(
        fps=fps,
        detection_rate=detection_rate,
        group_visibility_totals=group_visibility_totals,
        frames_with_pose=frames_with_pose,
        brightness_values=image_quality["brightness_values"],
        sharpness_values=image_quality["sharpness_values"],
        pose_movement_values=pose_movement_values,
        frame_change_values=image_quality["frame_change_values"],
        occupancy_values=occupancy_values,
        headroom_values=headroom_values,
        camera_view_results=camera_view_results,
    )

    readiness = recording_quality.get("analysis_readiness", {})
    ready = bool(readiness.get("ready", False))

    if ready:
        sprint_analysis = analyze_sprint_stream(
            stream, max_gap_ms=300, minimum_segment_frames=30
        )
        biomechanics = build_sprint_stream_report(sprint_analysis)
    else:
        biomechanics = {
            "status": "skipped",
            "reason": readiness.get(
                "rating",
                "Recording did not pass the analysis-readiness gate.",
            ),
        }

    return {
        "provider": "rtmpose",
        "video": {
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration_seconds": round(duration_seconds, 2),
        },
        "analysis": {
            "frames_with_pose": frames_with_pose,
            "detection_rate_percent": round(detection_rate, 2),
        },
        "recording_quality": recording_quality,
        "tracking_summary": timeline.get("summary"),
        "biomechanics": biomechanics,
    }
