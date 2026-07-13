import unittest

from app.services.pose_adapters.rtmpose_adapter import (
    RTMPoseAdapter,
)


class TestRTMPoseAdapter(unittest.TestCase):
    def test_supports_custom_keypoint_schema(self) -> None:
        adapter = RTMPoseAdapter(
            name_map={
                0: "left_heel",
                1: "left_toe",
            }
        )

        frame = adapter.adapt_frame(
            {
                "keypoints": [
                    [0.2, 0.8],
                    [0.3, 0.9],
                ],
                "keypoint_scores": [
                    0.95,
                    0.90,
                ],
            },
            frame_index=5,
            timestamp_ms=200,
        )

        self.assertEqual(
            frame.backend,
            "rtmpose",
        )

        self.assertEqual(
            frame.get(
                "left_toe"
            ).confidence,
            0.90,
        )


if __name__ == "__main__":
    unittest.main()
