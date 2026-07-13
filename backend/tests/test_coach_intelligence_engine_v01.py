import unittest

from app.services.coach.evaluator import (
    evaluate_coach_rules,
)
from app.services.coach.knowledge_base import (
    export_knowledge_base,
)
from app.services.coach.report import (
    build_coach_report,
)


def problem_metrics() -> dict:
    return {
        "ground_contact_ms": 151.0,
        "push_off_completion_score": 52.0,
        "hip_extension_deg": 128.0,
        "foot_offset_percent": 25.0,
        "front_side_score": 58.0,
        "recovery_velocity_dps": 510.0,
        "knee_lift_percent": 24.0,
        "trailing_distance_percent": 35.0,
        "back_side_duration_ms": 285.0,
        "heel_recovery_speed": 0.9,
        "cadence_cv_percent": 11.5,
        "contact_cv_percent": 13.0,
        "flight_cv_percent": 9.0,
        "vertical_oscillation_percent": 13.2,
        "pelvis_stability_score": 68.0,
        "mechanical_efficiency_score": 59.0,
    }


def confidences() -> dict:
    return {
        "ground_contact_ms": 0.91,
        "push_off_completion_score": 0.86,
        "hip_extension_deg": 0.90,
        "foot_offset_percent": 0.92,
        "front_side_score": 0.89,
        "recovery_velocity_dps": 0.87,
        "knee_lift_percent": 0.90,
        "trailing_distance_percent": 0.88,
        "back_side_duration_ms": 0.85,
        "heel_recovery_speed": 0.84,
        "cadence_cv_percent": 0.93,
        "contact_cv_percent": 0.90,
        "flight_cv_percent": 0.89,
        "vertical_oscillation_percent": 0.91,
        "pelvis_stability_score": 0.86,
        "mechanical_efficiency_score": 0.90,
    }


class TestCoachIntelligenceEngineV01(
    unittest.TestCase
):
    def test_rules_trigger_from_evidence(
        self,
    ) -> None:
        insights = evaluate_coach_rules(
            metrics=problem_metrics(),
            confidences=confidences(),
        )

        rule_ids = {
            insight.rule_id
            for insight in insights
        }

        self.assertIn(
            "sprint.long_contact_incomplete_push_off",
            rule_ids,
        )

        self.assertIn(
            "sprint.front_side_overstride",
            rule_ids,
        )

        self.assertIn(
            "sprint.excessive_back_side",
            rule_ids,
        )

    def test_report_prioritises_development(
        self,
    ) -> None:
        report = build_coach_report(
            metrics=problem_metrics(),
            confidences=confidences(),
            units={
                "ground_contact_ms": "ms",
                "hip_extension_deg": "deg",
            },
        )

        self.assertEqual(
            report["status"],
            "completed",
        )

        self.assertGreater(
            len(
                report[
                    "development_priorities"
                ]
            ),
            0,
        )

        self.assertGreater(
            len(
                report[
                    "training_focus"
                ]
            ),
            0,
        )

        self.assertIsNotNone(
            report["confidence"]
        )

    def test_strength_rule(
        self,
    ) -> None:
        report = build_coach_report(
            metrics={
                "mechanical_efficiency_score": 90.0,
                "front_side_score": 88.0,
                "back_side_score": 86.0,
                "symmetry_score": 94.0,
            },
            confidences={
                "mechanical_efficiency_score": 0.93,
                "front_side_score": 0.91,
                "back_side_score": 0.90,
                "symmetry_score": 0.94,
            },
        )

        self.assertGreater(
            len(
                report["strengths"]
            ),
            0,
        )

    def test_no_hallucinated_insight_when_data_missing(
        self,
    ) -> None:
        report = build_coach_report(
            metrics={},
        )

        self.assertEqual(
            report["status"],
            "insufficient_evidence",
        )

        self.assertEqual(
            len(
                report[
                    "development_priorities"
                ]
            ),
            0,
        )

    def test_knowledge_base_export(
        self,
    ) -> None:
        knowledge = export_knowledge_base()

        self.assertEqual(
            knowledge["event"],
            "sprint",
        )

        self.assertGreater(
            len(
                knowledge["rules"]
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
