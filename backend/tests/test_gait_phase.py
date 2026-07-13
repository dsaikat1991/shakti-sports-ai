import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_phase import (
    calculate_knee_symmetry,
    detect_knee_cycle_events,
)


def frame(
    index: int,
    left: float | None,
    right: float | None,
) -> FrameMetrics:
    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 100,
        joint_angles={
            "left_knee": left,
            "right_knee": right,
        },
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 90.0,
            "suitable_for_sprint": True,
        },
        landmarks=(),
    )


class TestGaitPhase(unittest.TestCase):
    def test_symmetry_score_is_high_for_matching_ranges(self) -> None:
        frames = [
            frame(0, 170.0, 168.0),
            frame(1, 120.0, 118.0),
            frame(2, 165.0, 163.0),
        ]

        result = calculate_knee_symmetry(frames)

        self.assertGreaterEqual(
            result["symmetry_score"],
            95.0,
        )

    def test_cycle_event_result_has_both_sides(self) -> None:
        frames = [
            frame(0, 170.0, 130.0),
            frame(1, 150.0, 150.0),
            frame(2, 110.0, 170.0),
            frame(3, 150.0, 150.0),
            frame(4, 170.0, 110.0),
        ]

        result = detect_knee_cycle_events(frames)

        self.assertIn("left", result)
        self.assertIn("right", result)


if __name__ == "__main__":
    unittest.main()
