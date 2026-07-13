import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
    summarize_joint_angles,
)


def make_frame(
    frame_index: int,
    left_knee: float | None,
    right_knee: float | None,
) -> FrameMetrics:
    return FrameMetrics(
        frame_index=frame_index,
        timestamp_ms=frame_index * 40,
        joint_angles={
            "left_knee": left_knee,
            "right_knee": right_knee,
        },
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 90.0,
            "suitable_for_sprint": True,
        },
        landmarks=(),
    )


class TestSprintAnalyzer(unittest.TestCase):
    def test_joint_angle_summary(self) -> None:
        frames = [
            make_frame(0, 160.0, 170.0),
            make_frame(1, 140.0, 150.0),
            make_frame(2, 120.0, None),
        ]

        result = summarize_joint_angles(frames)

        self.assertEqual(
            result["left_knee"]["frames_with_value"],
            3,
        )
        self.assertEqual(
            result["right_knee"]["frames_with_value"],
            2,
        )

    def test_skips_when_not_ready(self) -> None:
        result = build_sprint_biomechanics_preview(
            [],
            analysis_ready=False,
            readiness_reason="Unsuitable Camera Angle",
        )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(
            result["reason"],
            "Unsuitable Camera Angle",
        )


if __name__ == "__main__":
    unittest.main()
