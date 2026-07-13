import unittest

from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)


class TestSprintFlightCycleOutput(unittest.TestCase):
    def test_skipped_output_contains_new_sections(self) -> None:
        result = build_sprint_biomechanics_preview(
            [],
            analysis_ready=False,
            readiness_reason="Camera Angle Unclear",
        )

        self.assertEqual(
            result["flight_time"]["status"],
            "not_analyzed",
        )
        self.assertEqual(
            result["running_cycles"]["status"],
            "not_analyzed",
        )
        self.assertEqual(
            result["phase_timeline"]["status"],
            "not_analyzed",
        )


if __name__ == "__main__":
    unittest.main()
