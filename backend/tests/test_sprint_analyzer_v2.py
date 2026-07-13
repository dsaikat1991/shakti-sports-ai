import unittest

from app.services.athletics.models import (
    EventAnalysisRequest,
)
from app.services.athletics.sprint import (
    SprintEventAnalyzer,
)


class TestSprintAnalyzerV2(unittest.TestCase):
    def test_completed_result_contains_phase_output(self) -> None:
        timeline = [
            {
                "timestamp_ms": index * 100,
                "horizontal_progression": value,
            }
            for index, value in enumerate(
                [
                    0.00,
                    0.02,
                    0.06,
                    0.12,
                    0.20,
                    0.30,
                    0.42,
                    0.55,
                    0.68,
                    0.80,
                    0.91,
                    1.01,
                ]
            )
        ]

        result = SprintEventAnalyzer().analyze(
            EventAnalysisRequest(
                event="sprint"
            ),
            core_biomechanics={
                "status": "completed",
                "motion_timeline": timeline,
            },
        )

        self.assertEqual(
            result.status,
            "completed",
        )

        self.assertIn(
            "phases",
            result.phases,
        )


if __name__ == "__main__":
    unittest.main()
