import unittest

from app.services.athletics.models import (
    EventAnalysisRequest,
)
from app.services.athletics.router import (
    analyze_athletics_event,
)


class TestAthleticsRouter(unittest.TestCase):
    def test_routes_to_sprint_analyzer(self) -> None:
        result = analyze_athletics_event(
            EventAnalysisRequest(
                event="sprint",
            ),
            core_biomechanics={
                "status": "completed",
            },
        )

        self.assertEqual(
            result["event"],
            "sprint",
        )

        self.assertEqual(
            result["status"],
            "completed",
        )

    def test_routes_to_long_jump_analyzer(self) -> None:
        result = analyze_athletics_event(
            EventAnalysisRequest(
                event="long_jump",
            ),
            core_biomechanics={
                "status": "completed",
            },
        )

        self.assertEqual(
            result["event"],
            "long_jump",
        )

        self.assertIn(
            "takeoff",
            result["phases"]["target_phases"],
        )


if __name__ == "__main__":
    unittest.main()
