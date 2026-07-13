import unittest

from app.services.readiness.engine import (
    analyze_competition_readiness,
)
from app.services.readiness.flags import (
    build_readiness_flags,
)
from app.services.readiness.scoring import (
    readiness_status,
)


def ready_inputs() -> dict:
    return {
        "mechanical_efficiency_score": 89.0,
        "force_application_score": 88.0,
        "front_side_score": 87.0,
        "back_side_score": 84.0,
        "stability_pillar_score": 90.0,
        "fatigue_pattern_detected": False,
        "fatigue_evidence_count": 0,
        "recent_efficiency_change_percent": 4.0,
        "recent_ground_contact_change_percent": -3.0,
        "recent_cadence_change_percent": 2.0,
        "mechanical_efficiency_cv": 2.5,
        "cadence_cv_percent": 3.0,
        "contact_cv_percent": 4.0,
        "symmetry_score": 93.0,
        "critical_issues": 0,
        "high_issues": 0,
        "medium_issues": 1,
        "recording_quality_score": 91.0,
        "analysis_confidence_percent": 93.0,
        "valid_frame_percent": 95.0,
        "personal_best_detected": True,
        "mechanical_breakthrough_detected": True,
        "technical_confidences": [
            0.93,
            0.91,
        ],
        "physical_confidences": [
            0.90,
            0.89,
        ],
        "consistency_confidences": [
            0.92,
            0.90,
        ],
        "coach_confidences": [
            0.89,
        ],
    }


class TestCompetitionReadinessEngineV10(
    unittest.TestCase
):
    def test_status_mapping(
        self,
    ) -> None:
        self.assertEqual(
            readiness_status(
                96.0
            ),
            "peak_ready",
        )

        self.assertEqual(
            readiness_status(
                83.0
            ),
            "ready",
        )

        self.assertEqual(
            readiness_status(
                55.0
            ),
            "not_recommended",
        )

    def test_ready_profile(
        self,
    ) -> None:
        result = (
            analyze_competition_readiness(
                inputs=ready_inputs()
            )
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        readiness = result[
            "competition_readiness"
        ]

        self.assertGreater(
            readiness["score"],
            80.0,
        )

        self.assertIn(
            readiness["status"],
            {
                "ready",
                "competition_ready",
                "peak_ready",
            },
        )

        self.assertIn(
            "personal_best",
            readiness["flags"],
        )

        self.assertEqual(
            len(
                readiness[
                    "components"
                ]
            ),
            5,
        )

    def test_fatigue_and_issues_reduce_readiness(
        self,
    ) -> None:
        inputs = ready_inputs()

        inputs.update(
            {
                "mechanical_efficiency_score": 66.0,
                "force_application_score": 58.0,
                "fatigue_pattern_detected": True,
                "fatigue_evidence_count": 4,
                "recent_efficiency_change_percent": -8.0,
                "recent_ground_contact_change_percent": 9.0,
                "recent_cadence_change_percent": -7.0,
                "mechanical_efficiency_cv": 14.0,
                "cadence_cv_percent": 15.0,
                "contact_cv_percent": 17.0,
                "symmetry_score": 68.0,
                "critical_issues": 1,
                "high_issues": 2,
                "recording_quality_score": 74.0,
                "analysis_confidence_percent": 72.0,
                "valid_frame_percent": 70.0,
            }
        )

        result = (
            analyze_competition_readiness(
                inputs=inputs
            )
        )

        readiness = result[
            "competition_readiness"
        ]

        self.assertLess(
            readiness["score"],
            70.0,
        )

        self.assertIn(
            "possible_fatigue",
            readiness["flags"],
        )

    def test_flags(
        self,
    ) -> None:
        flags = build_readiness_flags(
            personal_best_detected=True,
            plateau_detected=True,
            fatigue_pattern_detected=False,
            technique_regression_detected=False,
            mechanical_breakthrough_detected=True,
            measurement_confidence_score=65.0,
        )

        self.assertIn(
            "personal_best",
            flags,
        )

        self.assertIn(
            "plateau_detected",
            flags,
        )

        self.assertIn(
            "low_measurement_confidence",
            flags,
        )

    def test_partial_input_support(
        self,
    ) -> None:
        result = (
            analyze_competition_readiness(
                inputs={
                    "mechanical_efficiency_score": 84.0,
                    "front_side_score": 82.0,
                    "back_side_score": 80.0,
                    "technical_confidences": [
                        0.90,
                    ],
                    "recording_quality_score": 88.0,
                    "analysis_confidence_percent": 90.0,
                    "valid_frame_percent": 92.0,
                }
            )
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertIsNotNone(
            result[
                "competition_readiness"
            ]["score"],
        )


if __name__ == "__main__":
    unittest.main()
