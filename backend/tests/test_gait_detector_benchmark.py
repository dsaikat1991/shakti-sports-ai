import unittest

from app.services.biomechanics.gait_detector_benchmark import (
    benchmark_detector_v3,
)
from app.services.biomechanics.gait_event_models import (
    GaitEvent,
)


class TestGaitDetectorBenchmark(unittest.TestCase):
    def test_benchmark_returns_metrics(self) -> None:
        result = benchmark_detector_v3(
            frame_metrics=[],
            actual_events=[
                GaitEvent(
                    event_type="initial_contact",
                    side="left",
                    timestamp_ms=1000,
                )
            ],
        )

        self.assertIn("overall", result)
        self.assertIn("by_event_type", result)


if __name__ == "__main__":
    unittest.main()
