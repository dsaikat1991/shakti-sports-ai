import unittest

from app.services.biomechanics.angles import (
    calculate_angle,
    calculate_joint_angle,
)


class TestAngleCalculation(unittest.TestCase):
    def test_straight_angle_is_180_degrees(self) -> None:
        angle = calculate_angle(
            (0.0, 0.0),
            (0.5, 0.0),
            (1.0, 0.0),
        )

        self.assertEqual(angle, 180.0)

    def test_right_angle_is_90_degrees(self) -> None:
        angle = calculate_angle(
            (0.0, 1.0),
            (0.0, 0.0),
            (1.0, 0.0),
        )

        self.assertEqual(angle, 90.0)

    def test_acute_angle_is_45_degrees(self) -> None:
        angle = calculate_angle(
            (1.0, 0.0),
            (0.0, 0.0),
            (1.0, 1.0),
        )

        self.assertEqual(angle, 45.0)

    def test_overlapping_points_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            calculate_angle(
                (0.0, 0.0),
                (0.0, 0.0),
                (1.0, 1.0),
            )

    def test_unreliable_landmark_returns_none(self) -> None:
        landmarks = [
            {
                "x": 0.0,
                "y": 0.0,
                "visibility": 1.0,
                "presence": 1.0,
            },
            {
                "x": 0.5,
                "y": 0.0,
                "visibility": 0.1,
                "presence": 1.0,
            },
            {
                "x": 1.0,
                "y": 0.0,
                "visibility": 1.0,
                "presence": 1.0,
            },
        ]

        result = calculate_joint_angle(
            landmarks,
            0,
            1,
            2,
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()