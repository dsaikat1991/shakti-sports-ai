from __future__ import annotations

from typing import Any

from app.services.biomechanics.angles import calculate_frame_joint_angles
from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)
from app.services.pose_adapters.compatibility import (
    to_legacy_landmark_list,
)
from app.services.pose_adapters.models import UnifiedPoseFrame
from app.services.pose_remote.pose_stream import (
    PoseSegment,
    PoseStream,
    fill_gaps,
    split_into_segments,
)
from app.services.quality.orientation import classify_camera_view
from app.services.quality.visibility import calculate_athlete_bounding_box

HALPE26_TO_MEDIAPIPE_INDEX: dict[str, int] = {
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
    "left_heel": 29,
    "right_heel": 30,
    "left_big_toe": 31,
    "right_big_toe": 32,
}

MEDIAPIPE_LANDMARK_COUNT = 33
DEFAULT_MINIMUM_SEGMENT_FRAMES = 30


def pose_frame_to_frame_metrics(
    frame: UnifiedPoseFrame,
) -> FrameMetrics:
    landmarks = to_legacy_landmark_list(
        frame,
        index_map=HALPE26_TO_MEDIAPIPE_INDEX,
        total_landmarks=MEDIAPIPE_LANDMARK_COUNT,
    )

    return FrameMetrics(
        frame_index=frame.frame_index,
        timestamp_ms=frame.timestamp_ms,
        joint_angles=calculate_frame_joint_angles(
            landmarks,
    backend=frame.backend,
        ),
        bounding_box=calculate_athlete_bounding_box(
            landmarks,
            backend=frame.backend,
        ),
        camera_view=classify_camera_view(
            landmarks,
            backend=frame.backend,
        ),
        landmarks=tuple(landmarks),
    )


def analyze_sprint_segment(
    segment: PoseSegment,
    *,
    minimum_frames: int = DEFAULT_MINIMUM_SEGMENT_FRAMES,
) -> dict[str, Any]:
    frame_metrics = [
        pose_frame_to_frame_metrics(frame)
        for frame in segment.frames
    ]
    ready = len(frame_metrics) >= minimum_frames
    reason = (
        "ok"
        if ready
        else (
            f"Segment has {len(frame_metrics)} frames; at least "
            f"{minimum_frames} are needed for sprint metrics."
        )
    )

    analysis = build_sprint_biomechanics_preview(
        frame_metrics,
        analysis_ready=ready,
        readiness_reason=reason,
    )
    analysis["segment"] = {
        "start_frame_index": segment.start_frame_index,
        "end_frame_index": segment.end_frame_index,
        "frame_count": segment.frame_count,
        "duration_ms": segment.duration_ms,
    }
    return analysis


def analyze_sprint_stream(
    stream: PoseStream,
    *,
    max_gap_ms: int = 300,
    minimum_segment_frames: int = DEFAULT_MINIMUM_SEGMENT_FRAMES,
) -> dict[str, Any]:
    filled = fill_gaps(stream, max_gap_ms=max_gap_ms)
    segments = split_into_segments(filled, minimum_frames=1)
    analyses = [
        analyze_sprint_segment(
            segment,
            minimum_frames=minimum_segment_frames,
        )
        for segment in segments
    ]

    return {
        "provider": "rtmpose",
        "fps": filled.fps,
        "observed_frames": filled.metadata.get("observed_frames", 0),
        "interpolated_frames": filled.metadata.get(
            "interpolated_frames",
            0,
        ),
        "unbridged_gaps": len(filled.gaps),
        "segments_analyzed": sum(
            1
            for analysis in analyses
            if analysis.get("status") != "skipped"
        ),
        "segments": analyses,
    }
