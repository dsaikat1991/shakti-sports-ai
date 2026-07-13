from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.services.quality.orientation import classify_camera_view
from app.services.quality.visibility import (
    calculate_athlete_bounding_box,
    calculate_body_group_visibility,
    landmark_is_usable,
)


def make_landmark(
    x: float,
    y: float,
    confidence: float,
) -> SimpleNamespace:
    return SimpleNamespace(
        x=x,
        y=y,
        z=0.0,
        visibility=confidence,
        presence=confidence,
        confidence=confidence,
    )


class TestBackendAwareQualityPatch(unittest.TestCase):
    def test_rtmpose_accepts_point_four(self) -> None:
        item = make_landmark(0.5, 0.5, 0.40)
        self.assertTrue(
            landmark_is_usable(
                item,
                backend="rtmpose",
            )
        )

    def test_mediapipe_rejects_point_four(self) -> None:
        item = make_landmark(0.5, 0.5, 0.40)
        self.assertFalse(
            landmark_is_usable(
                item,
                backend="mediapipe",
            )
        )

    def test_bounding_box_backend_parameter(self) -> None:
        items = [
            make_landmark(0.1, 0.2, 0.40),
            make_landmark(0.9, 0.2, 0.40),
            make_landmark(0.1, 0.8, 0.40),
            make_landmark(0.9, 0.8, 0.40),
        ]
        self.assertIsNotNone(
            calculate_athlete_bounding_box(
                items,
                backend="rtmpose",
            )
        )

    def test_visibility_backend_parameter(self) -> None:
        items = [
            make_landmark(0.5, 0.5, 0.40)
            for _ in range(33)
        ]
        result = calculate_body_group_visibility(
            items,
            backend="rtmpose",
        )
        self.assertEqual(result["hips"], 100.0)

    def test_orientation_backend_parameter(self) -> None:
        items = [
            make_landmark(0.0, 0.0, 0.0)
            for _ in range(33)
        ]
        items[11] = make_landmark(0.45, 0.30, 0.40)
        items[12] = make_landmark(0.55, 0.30, 0.40)
        items[23] = make_landmark(0.46, 0.70, 0.40)
        items[24] = make_landmark(0.54, 0.70, 0.40)

        result = classify_camera_view(
            items,
            backend="rtmpose",
        )
        self.assertNotEqual(result["view"], "Unknown")
        self.assertEqual(result["pose_backend"], "rtmpose")


if __name__ == "__main__":
    unittest.main()
