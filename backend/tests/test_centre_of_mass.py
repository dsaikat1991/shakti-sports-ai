import unittest

from app.services.biomechanics.centre_of_mass import (
    analyze_centre_of_mass,
    estimate_frame_centre,
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
    x_shift: float,
    y_shift: float,
) -> FrameMetrics:
    points = [
        landmark(0.5, 0.5)
        for _ in range(33)
    ]

    body_indices = (
        11,
        12,
        13,
        14,
        15,
        16,
        23,
        24,
        25,
        26,
        27,
        28,
    )

    for point_index in body_indices:
        points[point_index] = landmark(
            0.4 + x_shift,
            0.5 + y_shift,
        )

    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 33,
        joint_angles={},
        bounding_box={
            "height": 0.6,
        },
        camera_view={
            "view": "Side View",
            "confidence": 95.0,
            "suitable_for_sprint": True,
        },
        landmarks=tuple(points),
    )


class TestCentreOfMass(unittest.TestCase):
    def test_frame_centre_is_estimated(self) -> None:
        sample = estimate_frame_centre(
            make_frame(0, 0.0, 0.0)
        )

        self.assertIsNotNone(sample)
        self.assertAlmostEqual(
            sample.x,
            0.4,
            places=3,
        )

    def test_vertical_oscillation_is_reported(self) -> None:
        frames = [
            make_frame(index, index * 0.01, shift)
            for index, shift in enumerate(
                [0.00, 0.01, -0.01, 0.02, -0.02, 0.00, 0.01]
            )
        ]

        result = analyze_centre_of_mass(frames)

        self.assertEqual(
            result["status"],
            "experimental",
        )
        self.assertIsNotNone(
            result["vertical_oscillation_body_height_percent"]
        )


if __name__ == "__main__":
    unittest.main()
