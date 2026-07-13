import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_event_detector_v3 import (
    detect_gait_events_v3,
)


def landmark(
    x: float,
    y: float,
) -> dict[str, float]:
    return {
        "x": x,
        "y": y,
        "visibility": 1.0,
        "presence": 1.0,
    }


def make_frame(
    index: int,
    left_y: float,
    right_y: float,
) -> FrameMetrics:
    points = [
        landmark(0.5, 0.5)
        for _ in range(33)
    ]

    for joint_index in (27, 29, 31):
        points[joint_index] = landmark(
            0.4 + index * 0.002,
            left_y,
        )

    for joint_index in (28, 30, 32):
        points[joint_index] = landmark(
            0.6 + index * 0.002,
            right_y,
        )

    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 40,
        joint_angles={
            "left_knee": 150.0 - index,
            "right_knee": 145.0 + index,
        },
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 95.0,
            "suitable_for_sprint": True,
        },
        landmarks=tuple(points),
    )


class TestGaitEventDetectorV3(unittest.TestCase):
    def test_returns_config_and_debug(self) -> None:
        frames = [
            make_frame(index, left, right)
            for index, (left, right) in enumerate(
                [
                    (0.66, 0.82),
                    (0.70, 0.80),
                    (0.76, 0.74),
                    (0.84, 0.68),
                    (0.80, 0.66),
                    (0.72, 0.70),
                    (0.68, 0.78),
                    (0.72, 0.84),
                    (0.80, 0.80),
                    (0.84, 0.72),
                    (0.78, 0.68),
                    (0.70, 0.72),
                ]
            )
        ]

        result = detect_gait_events_v3(frames)

        self.assertIn("config", result)
        self.assertIn("debug", result)
        self.assertIn(
            result["status"],
            ("experimental", "insufficient_data"),
        )


if __name__ == "__main__":
    unittest.main()
