import unittest

from app.services.biomechanics.sprint_analyzer import (
    build_sprint_biomechanics_preview,
)


class TestSprintContactOutput(unittest.TestCase):
    def test_skipped_output_contains_ground_contact(self) -> None:
        result = build_sprint_biomechanics_preview(
            [],
            analysis_ready=False,
            readiness_reason="Camera Angle Unclear",
        )

        self.assertEqual(
            result["ground_contact"]["status"],
            "not_analyzed",
        )


if __name__ == "__main__":
    unittest.main()
