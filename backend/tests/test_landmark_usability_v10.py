import unittest
from dataclasses import dataclass

from app.services.pose.landmark_usability import (
    MEDIAPIPE_POLICY,
    RTMPOSE_POLICY,
    LandmarkUsabilityPolicy,
    filter_usable_landmarks,
    landmark_confidence,
    landmark_is_usable,
    policy_for_backend,
    usability_summary,
)
from app.services.pose.pose_quality_policy import (
    build_pose_quality_policy_report,
)


@dataclass
class Landmark:
    x: float = 0.0
    y: float = 0.0
    visibility: float = 0.0
    presence: float = 0.0
    confidence: float | None = None


class TestLandmarkUsabilityV10(unittest.TestCase):
    def test_rtmpose_034_rejected(self):
        self.assertFalse(
            landmark_is_usable({"confidence": 0.34}, backend="rtmpose")
        )

    def test_rtmpose_035_accepted(self):
        self.assertTrue(
            landmark_is_usable({"confidence": 0.35}, backend="rtmpose")
        )

    def test_rtmpose_bridge_fields_accepted(self):
        landmark = Landmark(visibility=0.40, presence=0.40)
        self.assertTrue(
            landmark_is_usable(landmark, backend="rtmpose")
        )

    def test_mediapipe_035_rejected(self):
        landmark = Landmark(visibility=0.35, presence=0.35)
        self.assertFalse(
            landmark_is_usable(landmark, backend="mediapipe")
        )

    def test_mediapipe_050_accepted(self):
        landmark = Landmark(visibility=0.50, presence=0.50)
        self.assertTrue(
            landmark_is_usable(landmark, backend="mediapipe")
        )

    def test_mediapipe_requires_both(self):
        landmark = Landmark(visibility=0.70, presence=0.40)
        self.assertFalse(
            landmark_is_usable(landmark, backend="mediapipe")
        )

    def test_explicit_confidence_override(self):
        landmark = {"confidence": 0.42}
        self.assertFalse(
            landmark_is_usable(
                landmark,
                backend="rtmpose",
                minimum_confidence=0.45,
            )
        )
        self.assertTrue(
            landmark_is_usable(
                landmark,
                backend="rtmpose",
                minimum_confidence=0.40,
            )
        )

    def test_custom_policy(self):
        policy = LandmarkUsabilityPolicy(
            backend="rtmpose",
            minimum_visibility=0.30,
            minimum_presence=0.30,
            minimum_confidence=0.30,
        )
        self.assertTrue(
            landmark_is_usable(
                {"confidence": 0.31},
                backend="rtmpose",
                policy=policy,
            )
        )

    def test_unknown_backend_uses_mediapipe_policy(self):
        self.assertEqual(
            policy_for_backend("unknown"),
            MEDIAPIPE_POLICY,
        )

    def test_policy_defaults(self):
        self.assertEqual(RTMPOSE_POLICY.minimum_confidence, 0.35)
        self.assertEqual(MEDIAPIPE_POLICY.minimum_visibility, 0.50)

    def test_confidence_reader(self):
        self.assertEqual(
            landmark_confidence(
                {"confidence": 0.61},
                backend="rtmpose",
            ),
            0.61,
        )

    def test_filter_usable_landmarks(self):
        landmarks = {
            "left_ankle": {"confidence": 0.60},
            "right_ankle": {"confidence": 0.20},
        }
        filtered = filter_usable_landmarks(
            landmarks,
            backend="rtmpose",
        )
        self.assertEqual(set(filtered), {"left_ankle"})

    def test_usability_summary(self):
        summary = usability_summary(
            {
                "a": {"confidence": 0.60},
                "b": {"confidence": 0.20},
            },
            backend="rtmpose",
        )
        self.assertEqual(summary["usable_landmarks"], 1)
        self.assertEqual(summary["usable_ratio"], 0.5)

    def test_policy_report(self):
        report = build_pose_quality_policy_report("rtmpose")
        self.assertEqual(report["minimum_confidence"], 0.35)
        self.assertEqual(report["backend"], "rtmpose")


if __name__ == "__main__":
    unittest.main()
