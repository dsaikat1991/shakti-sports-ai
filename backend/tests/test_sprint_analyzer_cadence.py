import unittest

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)


class TestSprintAnalyzerCadence(unittest.TestCase):
    def test_skipped_result_contains_cadence(self) -> None:
        result = build_sprint_biomechanics_preview(
            [],
            analysis_ready=False,
            readiness_reason="Unsuitable Camera Angle",
        )

        self.assertEqual(
            result["cadence"]["status"],
            "not_analyzed",
        )


if __name__ == "__main__":
    unittest.main()
