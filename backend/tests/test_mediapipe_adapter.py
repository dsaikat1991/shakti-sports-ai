import unittest

from app.services.pose_adapters.mediapipe_adapter import (
    MediaPipePoseAdapter,
)


class TestMediaPipeAdapter(unittest.TestCase):
    def test_maps_landmarks_to_unified_names(self) -> None:
        raw_pose = [
            {
                "x": index / 100,
                "y": index / 100,
                "z": 0.0,
                "visibility": 0.9,
                "presence": 0.8,
            }
            for index in range(33)
        ]

        frame = MediaPipePoseAdapter().adapt_frame(
            raw_pose,
            frame_index=10,
            timestamp_ms=333,
        )

        self.assertEqual(
            frame.backend,
            "mediapipe",
        )

        self.assertIsNotNone(
            frame.get("left_heel")
        )

        self.assertEqual(
            frame.get(
                "left_heel"
            ).source_index,
            29,
        )


if __name__ == "__main__":
    unittest.main()
