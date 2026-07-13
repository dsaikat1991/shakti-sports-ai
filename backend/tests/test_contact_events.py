import unittest

from app.services.biomechanics.contact_events import (
    detect_contact_events,
    summarize_contact_times,
)
from app.services.biomechanics.frame_metrics import FrameMetrics


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
        timestamp_ms=index * 33,
        joint_angles={},
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 95.0,
            "suitable_for_sprint": True,
        },
        landmarks=tuple(points),
    )


class TestContactEvents(unittest.TestCase):
    def test_detects_synthetic_contact_peaks(self) -> None:
        left = [
            0.70,
            0.72,
            0.76,
            0.82,
            0.88,
            0.84,
            0.78,
            0.73,
            0.71,
            0.74,
            0.80,
            0.87,
            0.83,
            0.77,
            0.72,
        ]

        right = [
            0.72,
            0.77,
            0.83,
            0.87,
            0.82,
            0.76,
            0.72,
            0.70,
            0.74,
            0.80,
            0.86,
            0.82,
            0.76,
            0.72,
            0.70,
        ]

        frames = [
            make_frame(index, left_y, right_y)
            for index, (left_y, right_y)
            in enumerate(zip(left, right))
        ]

        result = detect_contact_events(frames)

        self.assertIn("left", result)
        self.assertIn("right", result)

    def test_contact_summary_handles_no_events(self) -> None:
        summary = summarize_contact_times(
            {
                "left": [],
                "right": [],
            }
        )

        self.assertEqual(
            summary["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
