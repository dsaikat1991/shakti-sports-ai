import unittest

from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)


class TestSprintCentreOutput(unittest.TestCase):
    def test_skipped_output_contains_centre_of_mass(self) -> None:
        result = build_sprint_biomechanics_preview(
            [],
            analysis_ready=False,
            readiness_reason="Camera Angle Unclear",
        )

        self.assertEqual(
            result["centre_of_mass"]["status"],
            "not_analyzed",
        )


if __name__ == "__main__":
    unittest.main()
