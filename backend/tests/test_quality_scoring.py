import unittest

from app.services.quality.frame_quality import score_camera_height
from app.services.quality.scoring import build_quality_result


def good_side_view() -> dict:
    return {
        "view": "Side View",
        "confidence": 95.0,
        "suitable_for_sprint": True,
    }


def baseline_kwargs(*, headroom_values: list[float] | None) -> dict:
    """A recording that would otherwise pass every other quality check."""
    return {
        "fps": 30.0,
        "detection_rate": 100.0,
        "group_visibility_totals": {
            "head": 100.0 * 20,
            "shoulders": 100.0 * 20,
            "hips": 100.0 * 20,
            "knees": 100.0 * 20,
            "ankles": 100.0 * 20,
            "feet": 100.0 * 20,
        },
        "frames_with_pose": 20,
        "brightness_values": [120.0] * 10,
        "sharpness_values": [150.0] * 10,
        "pose_movement_values": [0.05] * 10,
        "frame_change_values": [5.0] * 9,
        "occupancy_values": [30.0] * 20,
        "camera_view_results": [good_side_view()] * 20,
        "headroom_values": headroom_values,
    }


class TestScoreCameraHeight(unittest.TestCase):
    def test_normal_headroom_scores_perfectly(self) -> None:
        self.assertEqual(score_camera_height(0.15), 100.0)
        self.assertEqual(score_camera_height(0.19), 100.0)

    def test_borderline_headroom_is_penalized(self) -> None:
        self.assertEqual(score_camera_height(0.28), 60.0)

    def test_low_camera_headroom_scores_low(self) -> None:
        # Matches the two known-bad clips' measured headroom (~0.33, ~0.41).
        self.assertEqual(score_camera_height(0.33), 30.0)
        self.assertEqual(score_camera_height(0.41), 10.0)


class TestBuildQualityResultCameraHeight(unittest.TestCase):
    def test_good_headroom_can_pass_biomechanics_ready(self) -> None:
        result = build_quality_result(**baseline_kwargs(headroom_values=[0.19] * 20))

        self.assertTrue(result["biomechanics_ready"])
        self.assertEqual(result["metrics"]["camera_height_score"], 100.0)

    def test_excessive_headroom_blocks_biomechanics_ready(self) -> None:
        # Same otherwise-perfect recording, only headroom changed.
        result = build_quality_result(**baseline_kwargs(headroom_values=[0.41] * 20))

        self.assertFalse(result["biomechanics_ready"])
        self.assertEqual(result["metrics"]["camera_height_score"], 10.0)
        self.assertTrue(
            any("angled upward" in warning for warning in result["warnings"])
        )
        self.assertTrue(
            any("waist-to-shoulder" in rec for rec in result["recommendations"])
        )

    def test_missing_headroom_values_does_not_crash_or_gate(self) -> None:
        result = build_quality_result(**baseline_kwargs(headroom_values=[]))

        self.assertIsNone(result["metrics"]["camera_height_score"])
        # Absence of the signal should not itself block readiness.
        self.assertTrue(result["biomechanics_ready"])


if __name__ == "__main__":
    unittest.main()
