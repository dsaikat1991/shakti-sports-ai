import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_signals import (
    extract_side_signals,
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
    left_foot_y: float,
) -> FrameMetrics:
    points = [
        landmark(0.5, 0.5)
        for _ in range(33)
    ]

    for joint_index in (27, 29, 31):
        points[joint_index] = landmark(
            0.4 + index * 0.01,
            left_foot_y,
        )

    for joint_index in (28, 30, 32):
        points[joint_index] = landmark(
            0.6,
            0.7,
        )

    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 33,
        joint_angles={
            "left_knee": 150.0 - index,
            "right_knee": 150.0,
        },
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 95.0,
            "suitable_for_sprint": True,
        },
        landmarks=tuple(points),
    )


class TestGaitSignals(unittest.TestCase):
    def test_extracts_velocity_signals(self) -> None:
        frames = [
            make_frame(0, 0.70),
            make_frame(1, 0.74),
            make_frame(2, 0.78),
        ]

        signals = extract_side_signals(
            frames,
            "left",
        )

        self.assertEqual(
            len(signals),
            3,
        )
        self.assertGreater(
            signals[1].foot_vy,
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
