import unittest

from app.services.pose_adapters.compatibility import (
    to_legacy_landmark_list,
)
from app.services.pose_adapters.models import (
    UnifiedKeypoint,
    UnifiedPoseFrame,
)


class TestPoseCompatibility(unittest.TestCase):
    def test_converts_unified_pose_to_indexed_landmarks(self) -> None:
        frame = UnifiedPoseFrame(
            backend="rtmpose",
            frame_index=0,
            timestamp_ms=0,
            keypoints=(
                UnifiedKeypoint(
                    name="left_ankle",
                    x=0.4,
                    y=0.8,
                    confidence=0.9,
                ),
            ),
        )

        landmarks = to_legacy_landmark_list(
            frame,
            index_map={
                "left_ankle": 27,
            },
            total_landmarks=33,
        )

        self.assertEqual(
            landmarks[27].x,
            0.4,
        )

        self.assertEqual(
            landmarks[27].visibility,
            0.9,
        )


if __name__ == "__main__":
    unittest.main()
