import math
import unittest

from app.services.pose_adapters.models import (
    UnifiedKeypoint,
    UnifiedPoseFrame,
)
from app.services.pose_remote.biomechanics_bridge import (
    HALPE26_TO_MEDIAPIPE_INDEX,
    analyze_sprint_segment,
    analyze_sprint_stream,
    pose_frame_to_frame_metrics,
)
from app.services.pose_remote.pose_stream import (
    PoseGap,
    PoseSegment,
    PoseStream,
)

FRAME_INTERVAL_MS = 33


def make_pose_frame(
    frame_index: int,
    *,
    ankle_phase: float = 0.0,
    confidence: float = 0.9,
) -> UnifiedPoseFrame:
    def kp(name: str, x: float, y: float) -> UnifiedKeypoint:
        return UnifiedKeypoint(name=name, x=x, y=y, confidence=confidence)

    left_y = 0.85 + 0.05 * math.sin(ankle_phase)
    right_y = 0.85 - 0.05 * math.sin(ankle_phase)
    keypoints = (
        kp("nose", 0.5, 0.2),
        kp("left_shoulder", 0.45, 0.35),
        kp("right_shoulder", 0.55, 0.35),
        kp("left_elbow", 0.42, 0.45),
        kp("right_elbow", 0.58, 0.45),
        kp("left_wrist", 0.40, 0.55),
        kp("right_wrist", 0.60, 0.55),
        kp("left_hip", 0.47, 0.55),
        kp("right_hip", 0.53, 0.55),
        kp("left_knee", 0.46, 0.70),
        kp("right_knee", 0.54, 0.70),
        kp("left_ankle", 0.45, left_y),
        kp("right_ankle", 0.55, right_y),
        kp("left_heel", 0.44, left_y + 0.02),
        kp("right_heel", 0.56, right_y + 0.02),
        kp("left_big_toe", 0.46, left_y + 0.03),
        kp("right_big_toe", 0.56, right_y + 0.03),
    )
    return UnifiedPoseFrame(
        backend="rtmpose",
        frame_index=frame_index,
        timestamp_ms=frame_index * FRAME_INTERVAL_MS,
        keypoints=keypoints,
        image_width=960,
        image_height=540,
    )


def make_running_segment(
    start_index: int, frame_count: int
) -> PoseSegment:
    return PoseSegment(
        frames=tuple(
            make_pose_frame(
                start_index + offset,
                ankle_phase=offset * 0.7,
            )
            for offset in range(frame_count)
        )
    )


class TestPoseFrameToFrameMetrics(unittest.TestCase):
    def test_landmarks_land_on_mediapipe_indices(self) -> None:
        metrics = pose_frame_to_frame_metrics(make_pose_frame(3))
        self.assertEqual(len(metrics.landmarks), 33)
        left_ankle = metrics.landmarks[HALPE26_TO_MEDIAPIPE_INDEX["left_ankle"]]
        self.assertAlmostEqual(left_ankle.x, 0.45)
        self.assertAlmostEqual(left_ankle.visibility, 0.9)
        # MediaPipe-only points (mouth, fingers) stay zeroed and unusable.
        self.assertEqual(metrics.landmarks[9].visibility, 0.0)
        self.assertEqual(metrics.frame_index, 3)
        self.assertEqual(metrics.timestamp_ms, 99)

    def test_joint_angles_and_quality_context_computed(self) -> None:
        metrics = pose_frame_to_frame_metrics(make_pose_frame(0))
        self.assertTrue(
            any("knee" in name for name in metrics.joint_angles)
        )
        self.assertIsNotNone(metrics.bounding_box)
        self.assertIn("view", str(metrics.camera_view).lower())


class TestAnalyzeSprintSegment(unittest.TestCase):
    def test_short_segment_is_skipped_with_reason(self) -> None:
        analysis = analyze_sprint_segment(make_running_segment(0, 5))
        self.assertEqual(analysis["status"], "skipped")
        self.assertIn("5 frames", analysis["reason"])
        self.assertEqual(analysis["segment"]["frame_count"], 5)

    def test_long_segment_completes(self) -> None:
        analysis = analyze_sprint_segment(make_running_segment(0, 45))
        self.assertEqual(analysis["status"], "completed")
        self.assertIn("cadence", analysis)
        self.assertIn("contact_events", analysis)
        self.assertEqual(analysis["segment"]["frame_count"], 45)


class TestAnalyzeSprintStream(unittest.TestCase):
    def test_cut_splits_analysis_into_independent_segments(self) -> None:
        first = make_running_segment(0, 45)
        second = make_running_segment(100, 45)
        missing = tuple(range(45, 100))
        stream = PoseStream(
            frames=first.frames + second.frames,
            gaps=(
                PoseGap(
                    frame_indices=missing,
                    timestamps_ms=tuple(
                        index * FRAME_INTERVAL_MS for index in missing
                    ),
                    reasons=("lost",) * len(missing),
                ),
            ),
            image_width=960,
            image_height=540,
            fps=30.0,
            metadata={"observed_frames": 90, "interpolated_frames": 0},
        )

        result = analyze_sprint_stream(stream)

        self.assertEqual(result["provider"], "rtmpose")
        self.assertEqual(result["unbridged_gaps"], 1)
        self.assertEqual(len(result["segments"]), 2)
        self.assertEqual(result["segments_analyzed"], 2)
        for analysis in result["segments"]:
            self.assertEqual(analysis["status"], "completed")
        self.assertEqual(
            result["segments"][0]["segment"]["end_frame_index"], 44
        )
        self.assertEqual(
            result["segments"][1]["segment"]["start_frame_index"], 100
        )


if __name__ == "__main__":
    unittest.main()
