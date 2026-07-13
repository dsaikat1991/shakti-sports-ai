import unittest

from app.services.sprint.mechanical_efficiency_engine import (
    analyze_mechanical_efficiency,
)
from app.services.sprint.mechanical_efficiency_explainability import (
    build_efficiency_explanation,
)
from app.services.sprint.mechanical_efficiency_scoring import (
    rating_for_score,
    score_inverse_range,
    weighted_mean,
)


def strong_inputs() -> dict:
    return {
        "ground_contact_ms": 102.0,
        "push_off_completion_score": 88.0,
        "hip_extension_deg": 155.0,
        "com_acceleration_score": 86.0,
        "shin_angle_deg": 70.0,
        "cadence_spm": 286.0,
        "cadence_cv_percent": 2.5,
        "contact_cv_percent": 3.5,
        "flight_cv_percent": 4.5,
        "cycle_consistency_score": 92.0,
        "front_side_score": 88.0,
        "knee_lift_percent": 44.0,
        "recovery_velocity_dps": 780.0,
        "foot_offset_percent": 6.0,
        "back_side_score": 84.0,
        "trailing_distance_percent": 12.0,
        "heel_recovery_speed": 1.9,
        "back_side_duration_ms": 145.0,
        "vertical_oscillation_percent": 5.8,
        "pelvis_stability_score": 90.0,
        "trunk_stability_score": 87.0,
        "symmetry_score": 93.0,
        "force_confidences": [
            0.94,
            0.91,
        ],
        "rhythm_confidences": [
            0.92,
            0.90,
        ],
        "front_side_confidences": [
            0.93,
            0.91,
        ],
        "back_side_confidences": [
            0.90,
            0.89,
        ],
        "stability_confidences": [
            0.92,
            0.90,
        ],
    }


class TestMechanicalEfficiencyEngineV01(
    unittest.TestCase
):
    def test_scoring_helpers(
        self,
    ) -> None:
        self.assertEqual(
            score_inverse_range(
                100.0,
                ideal_max=110.0,
                poor_max=180.0,
            ),
            100.0,
        )

        self.assertEqual(
            weighted_mean(
                [
                    (80.0, 0.5),
                    (100.0, 0.5),
                ]
            ),
            90.0,
        )

        self.assertEqual(
            rating_for_score(
                91.0
            ),
            "excellent",
        )

    def test_returns_weighted_efficiency_score(
        self,
    ) -> None:
        result = (
            analyze_mechanical_efficiency(
                inputs=strong_inputs()
            )
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        efficiency = result[
            "mechanical_efficiency"
        ]

        self.assertGreater(
            efficiency["score"],
            80.0,
        )

        self.assertEqual(
            len(
                efficiency[
                    "pillars"
                ]
            ),
            5,
        )

        self.assertIsNotNone(
            efficiency[
                "confidence"
            ]
        )

    def test_poor_mechanics_reduce_score(
        self,
    ) -> None:
        inputs = strong_inputs()
        inputs.update(
            {
                "ground_contact_ms": 175.0,
                "push_off_completion_score": 35.0,
                "cadence_cv_percent": 14.0,
                "contact_cv_percent": 17.0,
                "front_side_score": 42.0,
                "foot_offset_percent": 30.0,
                "back_side_score": 38.0,
                "trailing_distance_percent": 42.0,
                "back_side_duration_ms": 330.0,
                "vertical_oscillation_percent": 15.0,
                "symmetry_score": 62.0,
            }
        )

        result = (
            analyze_mechanical_efficiency(
                inputs=inputs
            )
        )

        self.assertLess(
            result[
                "mechanical_efficiency"
            ]["score"],
            65.0,
        )

    def test_explainability(
        self,
    ) -> None:
        result = (
            analyze_mechanical_efficiency(
                inputs=strong_inputs()
            )
        )

        explanation = (
            build_efficiency_explanation(
                result
            )
        )

        self.assertEqual(
            explanation[
                "validation_level"
            ],
            "experimental",
        )

        self.assertGreater(
            len(
                explanation[
                    "strengths"
                ]
            ),
            0,
        )

    def test_partial_inputs_are_supported(
        self,
    ) -> None:
        result = (
            analyze_mechanical_efficiency(
                inputs={
                    "front_side_score": 82.0,
                    "front_side_confidences": [
                        0.9,
                    ],
                    "back_side_score": 78.0,
                    "back_side_confidences": [
                        0.88,
                    ],
                }
            )
        )

        self.assertEqual(
            result["status"],
            "experimental",
        )

        self.assertIsNotNone(
            result[
                "mechanical_efficiency"
            ]["score"],
        )


if __name__ == "__main__":
    unittest.main()
