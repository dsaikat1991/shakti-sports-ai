import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_event_detector_v2 import (
    detect_gait_events_v2,
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
            0.4,
            left_y,
        )

    for joint_index in (28, 30, 32):
        points[joint_index] = landmark(
            0.6,
            right_y,
        )

    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 40,
        joint_angles={
            "left_knee": 140.0,
            "right_knee": 140.0,
        },
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 95.0,
            "suitable_for_sprint": True,
        },
        landmarks=tuple(points),
    )


class TestGaitEventDetectorV2(unittest.TestCase):
    def test_returns_expected_structure(self) -> None:
        frames = [
            make_frame(index, left_y, right_y)
            for index, (left_y, right_y)
            in enumerate(
                [
                    (0.65, 0.80),
                    (0.70, 0.78),
                    (0.78, 0.72),
                    (0.84, 0.68),
                    (0.80, 0.66),
                    (0.72, 0.70),
                    (0.68, 0.78),
                    (0.72, 0.84),
                    (0.80, 0.80),
                    (0.84, 0.72),
                ]
            )
        ]

        result = detect_gait_events_v2(frames)

        self.assertIn(
            result["status"],
            ("experimental", "insufficient_data"),
        )
        self.assertIn(
            "events",
            result,
        )
        self.assertIn(
            "debug",
            result,
        )


if __name__ == "__main__":
    unittest.main()
