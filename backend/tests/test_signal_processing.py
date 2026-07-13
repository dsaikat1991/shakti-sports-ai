import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.signal_processing import (
    prepare_angle_series,
    robust_angle_summary,
)


def frame(index: int, angle: float | None) -> FrameMetrics:
    return FrameMetrics(
        frame_index=index,
        timestamp_ms=index * 33,
        joint_angles={"left_knee": angle},
        bounding_box=None,
        camera_view={
            "view": "Side View",
            "confidence": 90.0,
            "suitable_for_sprint": True,
        },
        landmarks=(),
    )


class TestSignalProcessing(unittest.TestCase):
    def test_outlier_is_removed(self) -> None:
        frames = [
            frame(0, 160.0),
            frame(1, 158.0),
            frame(2, 157.0),
            frame(3, 20.0),
            frame(4, 156.0),
            frame(5, 155.0),
            frame(6, 154.0),
        ]

        series = prepare_angle_series(frames, "left_knee")
        values = [sample.angle_degrees for sample in series]

        self.assertGreater(min(values), 100.0)

    def test_summary_uses_percentiles(self) -> None:
        frames = [
            frame(index, float(value))
            for index, value in enumerate(
                [100, 110, 120, 130, 140, 150, 160]
            )
        ]

        series = prepare_angle_series(frames, "left_knee")
        summary = robust_angle_summary(series)

        self.assertIsNotNone(summary["p05_degrees"])
        self.assertIsNotNone(summary["p95_degrees"])


if __name__ == "__main__":
    unittest.main()
